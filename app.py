import streamlit as st
from google import genai
from dotenv import load_dotenv
import json
import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid
import pandas as pd
import time


load_dotenv()
api_key = os.getenv('API_KEY_GENAI')
genai_client = genai.Client(api_key=api_key)
url_supabase = os.getenv('URL_SUPABASE')
key_supabase = os.getenv('KEY_SUPABASE')

supabase = create_client(url_supabase, key_supabase) 

def gerar_perguntas(tema): 
    response = genai_client.models.generate_content(
        model='gemini-1.5-flash',
        contents=f'Faça 5 perguntas sobre esse tema {tema}, cada pergunta deve conter 4 alternativas e suas respectivas explicações, me de em json a reposta do prompt, no json deve conter a chave chamada pergunta, uma chave chamada respostas e uma chave chamada explicações com as 4 alternativas sem nomear elas de A a B ou de 1 a 4 e a chave chamada resposta_correta dizendo qual resposta a correta, mas quero a resposta correta em texto da resposta, não o index que a resposta ta, e traz um titulo sobre o tema do quiz tipo Quiz sobre ai vem o nome do tema e depois um emoji a chave pode ter nome de titulo'
    ).to_json_dict() 
    return str(response['candidates'][0]['content']['parts'][0]['text']).replace('```', '').replace('json', '')


def final_quiz(pontuacao):
    st.set_page_config(layout='centered')
    st.markdown("""
                    <style>
                    .block-container {
                        padding-top: 1.2rem; 
                        padding-bottom: 1rem;
                        text-align: center;
                    }
                    </style>
                """, unsafe_allow_html=True)
    image_path = "images/img-bee-movie.jpg"
    with st.container(horizontal_alignment='center'):
        st.title('Quiz finalizado!! Parabéns!!', width='content')
        if pontuacao >= 4:
            st.balloons()
            st.markdown(f"## Pontuação :green[{pontuacao}/5]", width='content')
            st.markdown("##### 🔥 Mandou muito bem! Você dominou o quiz e mostrou que tá por dentro do assunto!", width='content')
            st.image(image_path, caption='Parabéns!', width=715)
        elif pontuacao >= 2:
            st.markdown(f"## Pontuação :orange[{pontuacao}/5]", width='content')
            st.markdown("##### 👌 Foi bem! Mas dá pra melhorar, que tal tentar mais uma vez e subir sua pontuação?", width='content')
            st.image(image_path, caption='Parabéns!', width=715)
        else:
            st.markdown(f"## Pontuação :red[{pontuacao}/5]", width='content')
            st.markdown("##### 😅 Não foi dessa vez... mas cada tentativa é um aprendizado! Bora de novo?", width='content')
            st.image(image_path, caption='Parabéns!', width=715)
            
        if st.button(label='Reiniciar o Quiz'):
            st.session_state.pagina_atual = "home"
            st.session_state.tema_escolhido = None
            st.session_state.perguntas = None
            st.session_state.quiz_iniciado = True
            st.session_state.numero_pergunta = 0
            st.session_state.respondeu_pergunta = False
            st.session_state.resposta_respondida = ''
            st.session_state.index_resposta_respondida = 0
            st.session_state.pontuacao = 0
            st.rerun()

def jogar_quiz(perguntas, pagina):
    if pagina == 'quiz':
        
        json_perguntas = json.loads(perguntas)
        
        if 'quiz_iniciado' not in st.session_state:
            st.session_state.quiz_iniciado = True
        if 'numero_pergunta' not in st.session_state:
            st.session_state.numero_pergunta = 0
        if 'respondeu_pergunta' not in st.session_state:
            st.session_state.respondeu_pergunta = False
        if 'resposta_respondida' not in st.session_state:
            st.session_state.resposta_respondida = ''
        if 'index_resposta_respondida' not in st.session_state:
            st.session_state.index_resposta_respondida = 0
        if 'pontuacao' not in st.session_state:
            st.session_state.pontuacao = 0
            
        if st.session_state.quiz_iniciado:
            st.set_page_config(layout='centered')
            st.markdown("""
                    <style>
                    .block-container {
                        padding-top: 2.2rem; 
                        padding-bottom: 1rem;
                    }
                    </style>
                """, unsafe_allow_html=True)
            st.markdown('## ' + json_perguntas['titulo'])
            with st.container(border=True, horizontal_alignment='center'):
                st.markdown(f'### Pergunta {st.session_state.numero_pergunta + 1}/5')
                st.markdown('#### ' + json_perguntas['perguntas'][st.session_state.numero_pergunta]['pergunta'])
                for index,resposta in enumerate(json_perguntas['perguntas'][st.session_state.numero_pergunta]['respostas']):
                    if st.button(label=resposta, key=f'resposta_{index}', use_container_width=True, disabled=st.session_state.respondeu_pergunta):
                        st.session_state.resposta_respondida = resposta
                        st.session_state.index_resposta_respondida = index
                        st.session_state.respondeu_pergunta = True  
                        if resposta == json_perguntas['perguntas'][st.session_state.numero_pergunta]['resposta_correta']:
                            st.session_state.pontuacao += 1
                        st.rerun()
                
                
                if st.session_state.respondeu_pergunta == True:
                    resposta = st.session_state.resposta_respondida
                    index = st.session_state.index_resposta_respondida
                    if resposta == json_perguntas['perguntas'][st.session_state.numero_pergunta]['resposta_correta']:
                        st.success(
                                f"🎉 Parabéns!!! Você acertou!\n\n"
                                f"💡 Explicação: {json_perguntas['perguntas'][st.session_state.numero_pergunta]['explicações'][index]}"
                        )
                    else:
                        st.error(
                            f"❌ Ops! Resposta errada.\n\n"
                            f"✅ A resposta certa era **{json_perguntas['perguntas'][st.session_state.numero_pergunta]['resposta_correta']}**.\n\n"
                            f"💡 Explicação: {json_perguntas['perguntas'][st.session_state.numero_pergunta]['explicações'][index]}"
                        )  
                        
                    if st.session_state.respondeu_pergunta != False and st.session_state.numero_pergunta <= 3:
                        if st.button(label='Próxima Pergunta', key=f'pergunta_{st.session_state.numero_pergunta}'):
                            st.session_state.respondeu_pergunta = False
                            st.session_state.numero_pergunta += 1
                            st.rerun()
                    elif st.session_state.respondeu_pergunta != False and st.session_state.numero_pergunta == 4:
                        if st.button(label='Terminar quiz', key=f'btn_terminar_quiz_{st.session_state.numero_pergunta}'):
                            st.session_state.quiz_iniciado = False
                            st.session_state.numero_pergunta = 0
                            st.session_state.respondeu_pergunta = False
                            st.session_state.index_resposta_respondida = 0
                            st.rerun()
        else:                    
            final_quiz(st.session_state.pontuacao)
            
def iniciar_quiz():
    st.set_page_config(page_title='Quiz | Bee Smart', page_icon='🐝', layout='wide')
    
    if 'tema_escolhido' not in st.session_state:
        st.session_state.tema_escolhido = None
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = 'home'
    if 'perguntas' not in st.session_state:
        st.session_state.perguntas = None
    
    
    if st.session_state.pagina_atual == 'home':
        with st.container(vertical_alignment='center', horizontal_alignment='center'):
            st.markdown('# Seja bem-vindo ao Quiz :orange[Bee Smart] 🐝', width='content')
            st.markdown('### O Quiz que irá te ajudar a testar seus conhecimentos com qualquer **TEMA**!!!', width='content')
            col_regra1, col_regra2, col_regra3 = st.columns(3, )
            with col_regra1:
                st.info(
                    "**🐝 Dica da Bee**\n\n"
                    "**Seja específico!** Em vez de 'Python', tente 'Manipulação de arrays com NumPy'. Quanto mais nichado o tema, mais precisos serão os desafios. As perguntas são geradas por IA."
                )
            with col_regra2:
               st.info(
                    "**🎲 Curiosidade do Quiz**\n\n"
                    "**As perguntas são geradas via IA.** Nosso algoritmo analisa os conceitos centrais "
                    "do tema que você digitou para criar um quiz único e desafiador. Ótimo para treinar! 🤓"
                )
            with col_regra3:
                st.info(
                            "**🚀 Truque Rápido**\n\n"
                            "**Revisão com um clique!** Use os temas recentes para reforçar um conceito antes de uma prova "
                            "ou para solidificar o conhecimento de uma nova tecnologia."
                        )
            
            st.markdown('#### ⇩ Insira abaixo o tema no qual você irá jogar ⇩', width='content')
            
            tema_input = st.text_input('', placeholder='Digite o tema aqui', label_visibility='collapsed') 
            temas_anteriores = st.pills('Temas anteriores', ['IA', 'Python', 'Java'], selection_mode='single', label_visibility='collapsed')
            tema_selecionado = tema_selecionado = tema_input.strip() if tema_input.strip() else (temas_anteriores if temas_anteriores else None)
            
            if st.session_state.tema_escolhido == None and tema_selecionado:
                st.session_state.tema_escolhido = tema_selecionado
                st.rerun()

            if st.session_state.tema_escolhido != None:
                with st.spinner(text=f'Aguarde a IA gerar suas perguntas sobre o tema {st.session_state.tema_escolhido}...'):
                    st.session_state.perguntas = gerar_perguntas(st.session_state.tema_escolhido)
                    if st.session_state.perguntas != None:
                        st.session_state.pagina_atual = 'quiz'
                        st.rerun()
                                                     
    elif st.session_state.pagina_atual == 'quiz':
        jogar_quiz(st.session_state.perguntas, st.session_state.pagina_atual)

def tela_cadastro():
    st.title("Cadastro")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        foto = st.file_uploader("Foto de perfil", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Cadastrar")
        
        if submitted:
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": senha
            })
            
            if auth_response.user:
                user_id = auth_response.user.id
                foto_url = None
                
                if foto is not None:
                    caminho = f"perfil/{uuid.uuid4()}_{foto.name}"
                    foto_bytes = foto.read()
                    supabase.storage.from_("perfil").upload(caminho, foto_bytes)
                    foto_url = supabase.storage.from_("perfil").get_public_url(caminho)
                
                supabase.table("usuario").insert({
                    "id": user_id,
                    "nome": nome,
                    "foto_perfil": foto_url
                }).execute()
                

                st.success("Cadastro realizado! Verifique seu email para confirmar a conta.")
                time.sleep(5)  
                st.session_state['pagina_atual'] = "login"
                st.rerun()
            else:
                st.error("Erro ao cadastrar usuário!")

def tela_login():
    st.title("Login")
    with st.form("form_login"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            try:
                auth_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": senha
                })
                
                if auth_response.user:
                    st.session_state["user"] = auth_response.user
                    st.success(f"Bem-vindo, {email}!")
                    st.session_state['pagina_atual'] = "home"
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos")
            except Exception as e:
                if "Email not confirmed" in str(e):
                    st.warning("Confirme seu email antes de fazer login! Verifique sua caixa de entrada.")
                else:
                    st.error(f"Erro ao logar: {e}")
                
    if st.button("Não tem conta? Cadastre-se"):
        st.session_state['pagina_atual'] = "cadastro"
        st.rerun()
    
    if st.button("Esqueci minha senha"):
        st.session_state['pagina_atual'] = "recuperar_senha"
        st.rerun()

def tela_recuperar_senha():
    st.title("Recuperar Senha")
    with st.form("form_recuperar"):
        email = st.text_input("Digite seu email")
        submitted = st.form_submit_button("Enviar link de recuperação")
        if submitted:
            try:
                supabase.auth.reset_password_for_email(email)
                st.success("Email de recuperação enviado! Verifique sua caixa de entrada.")
            except Exception as e:
                st.error(f"Erro: {e}")

if __name__ == '__main__':
    if 'user' not in st.session_state:
        if st.session_state.get('pagina_atual') == "cadastro":
            tela_cadastro()
        else:
            tela_login()
    else:
        iniciar_quiz()