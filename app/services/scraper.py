import asyncio
import httpx
from bs4 import BeautifulSoup
from app.core.config import Settings

# Cabeçalhos comuns para as requisições
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0 (Edition std-1)',
    'authority': 'consulta-crf.caixa.gov.br',
    'scheme': 'https',
}


class FGTSServiceError(Exception):
    """Exceção customizada para erros no serviço de scraping."""
    pass


async def get_initial_info(client: httpx.AsyncClient) -> dict:
    """Busca a página inicial para obter cookies, ViewState e o captcha."""
    url = 'https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf'
    try:
        response = await client.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        view_state_tag = soup.find('input', {'name': 'javax.faces.ViewState'})
        img_tag = soup.select_one('div.captcha-imagem img')

        if not view_state_tag or not img_tag or 'value' not in view_state_tag.attrs or 'src' not in img_tag.attrs:
            raise FGTSServiceError("Não foi possível encontrar ViewState ou imagem do captcha na página.")

        return {
            "cookies": response.cookies,
            "view_state": view_state_tag['value'],
            "captcha_base64": img_tag['src']
        }
    except httpx.RequestError as e:
        raise FGTSServiceError(f"Erro de rede ao acessar a página inicial: {e}")


async def solve_captcha(client: httpx.AsyncClient, captcha_base64: str, api_key: str) -> str:
    """Envia o captcha para o serviço 2captcha e aguarda a resolução."""
    try:
        # Envia o captcha para ser resolvido
        in_response = await client.post('http://2captcha.com/in.php', data={
            'key': api_key, 'method': 'base64', 'body': captcha_base64,
            'regsense': 1, 'json': 1
        }, timeout=30)
        in_response.raise_for_status()
        request_id = in_response.json().get('request')

        if not request_id:
            raise FGTSServiceError("Falha ao enviar captcha para o serviço de resolução.")

        # Aguarda a resolução
        url_result = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
        for _ in range(15):  # Tenta por até 75 segundos
            await asyncio.sleep(5)
            res_response = await client.get(url_result, timeout=30)
            res_response.raise_for_status()
            result = res_response.json()
            if result.get('status') == 1:
                return result.get('request')

        raise FGTSServiceError("Tempo de espera para resolução do captcha esgotado.")

    except httpx.RequestError as e:
        raise FGTSServiceError(f"Erro de rede ao comunicar com o serviço de captcha: {e}")


async def submit_fgts_query(client: httpx.AsyncClient, cnpj: str, initial_info: dict, captcha_text: str) -> dict:
    """Submete o formulário com o CNPJ e o captcha resolvido."""
    url = 'https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf'

    headers = {**HEADERS, 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    form_data = {
        'mainForm': 'mainForm',
        'mainForm:tipoEstabelecimento': '1',
        'mainForm:txtCaptcha': captcha_text,
        'AJAXREQUEST': '_viewRoot',
        'mainForm:uf': '',
        'javax.faces.ViewState': initial_info['view_state'],
        'mainForm:btnConsultar': 'mainForm:btnConsultar',
        'mainForm:txtInscricao1': cnpj
    }

    try:
        response = await client.post(url, headers=headers, data=form_data, cookies=initial_info['cookies'], timeout=50)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        feedback_div = soup.find('div', class_='feedback')

        if not feedback_div:
            raise FGTSServiceError("Não foi possível encontrar o feedback na resposta da consulta.")

        feedback_text = feedback_div.get_text(strip=True)

        # --- Lógica de parsing melhorada ---

        if 'REGULAR perante o FGTS' in feedback_text:
            valores = soup.find_all('span', class_='valor')
            return {
                "cnpj": valores[0].get_text(strip=True),
                "razao_social": valores[1].get_text(strip=True),
                "resultado": "A empresa informada está REGULAR perante o FGTS."
            }
        elif 'não são suficientes para a comprovação' in feedback_text:
            valores = soup.find_all('span', class_='valor')
            return {
                "cnpj": valores[0].get_text(strip=True),
                "razao_social": valores[1].get_text(strip=True),
                "resultado": "A empresa informada está IRREGULAR perante o FGTS."
            }
        elif 'Código Captcha Inválido' in feedback_text:
            return {"resultado": "Captcha inválido. Tente novamente."}

        # === NOVO TRATAMENTO PARA CNPJ NÃO ENCONTRADO ===
        elif 'informar o CNPJ correto' in feedback_text:
            return {"resultado": "CNPJ não encontrado na base de dados do FGTS."}

        else:
            # Caso genérico para qualquer outra mensagem não esperada
            return {"resultado": feedback_text}

    except httpx.RequestError as e:
        raise FGTSServiceError(f"Erro de rede ao submeter a consulta: {e}")