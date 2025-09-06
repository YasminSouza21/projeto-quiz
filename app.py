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
from datetime import datetime
from urllib.parse import quote
import dashboard as dashboard
import re

load_dotenv()
api_key = os.getenv('API_KEY_GENAI')
genai_client = genai.Client(api_key=api_key)
url_supabase = os.getenv('URL_SUPABASE')
key_supabase = os.getenv('KEY_SUPABASE')

supabase = create_client(url_supabase, key_supabase) 

def tela_cadastro():
    st.markdown("""
                <style>
                .block-container {
                    padding-top: 1.6rem; 
                    padding-bottom: 0.2rem;
                }
                div .stHorizontalBlock{
                    display: flex;
                }
                .st-emotion-cache-1permvm{
                    gap: 0rem;
                }
                .st-emotion-cache-18tdrd9 h1{
                    padding: 0px 0px 10px 0px;
                }
                .st-emotion-cache-wfksaw{
                    gap: 5px;
                }
                button .e1hznt4w0{
                    font-size: 0.8rem;
                }
                </style>
            """, unsafe_allow_html=True)
    st.title("Cadastro")
    st.set_page_config(page_title='Cadastro | Bee Smart', page_icon='🐝', layout='wide')
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Cadastrar")
        
        if submitted:
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                st.error("Email inválido!")
                st.stop()
            if len(senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres!")
                st.stop()
            if len(nome.strip()) == 0:
                st.error("O nome não pode estar vazio!")
                st.stop()

            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": senha
            })
            
            if auth_response.user:
                user_id = auth_response.user.id

                supabase.table("usuario").insert({
                    "id": user_id,
                    "nome": nome
                }).execute()
                
                st.success("Cadastro realizado! Verifique seu email para confirmar a conta.")
                time.sleep(5)  
                st.session_state['pagina_atual'] = "login"
                st.rerun()
            else:
                st.error("Erro ao cadastrar usuário!")

def tela_login():
    st.markdown("""
                <style>
                .block-container {
                    padding-top:1.5rem; 
                    padding-bottom: -10rem;
                }
                #stToolbarActions{
                    height: 100px
                }
                #login{
                    padding: 0px 0px 10px 0px;   
                }
                button .e1hznt4w0{
                    font-size: 0.8rem;
                }
                .st-emotion-cache-wfksaw{
                    gap: 5px;
                }
                .st-emotion-cache-1permvm{
                    gap:0px;
                }
                </style>
            """, unsafe_allow_html=True)
    st.title("Login")
    st.set_page_config(page_title='Login | Bee Smart', page_icon='🐝', layout='wide')
    with st.form("form_login"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            erro = False

            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                st.error("Email inválido!")
                erro = True
            if len(senha.strip()) == 0:
                st.error("A senha não pode estar vazia!")
                erro = True

            if not erro: 
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


def gerar_perguntas(tema): 
    response = genai_client.models.generate_content(
        model='gemini-1.5-flash',
        contents=f'Faça 10 perguntas sobre esse tema {tema}, cada pergunta deve conter 4 alternativas e suas respectivas explicações, me de em json a reposta do prompt, no json deve conter a chave chamada pergunta, uma chave chamada respostas e uma chave chamada explicações com as 4 alternativas sem nomear elas de A a B ou de 1 a 4 e a chave chamada resposta_correta dizendo qual resposta a correta, mas quero a resposta correta em texto da resposta, não o index que a resposta ta, e traz um titulo sobre o tema do quiz tipo Quiz sobre ai vem o nome do tema e depois um emoji a chave pode ter nome de titulo'
    ).to_json_dict() 
    return str(response['candidates'][0]['content']['parts'][0]['text']).replace('```', '').replace('json', '')

def final_quiz(pontuacao):
    st.set_page_config(page_title='Final Quiz | Bee Smart', page_icon='🐝', layout='centered')
    st.markdown("""
                    <style>
                    .block-container {
                        padding-top: 1.2rem; 
                        padding-bottom: 1rem;
                        text-align: center;
                    }
                    @media (max-width: 600px){
                        img{
                            width: 334px;
                        }
                        st-emotion-cache-uxneyj e1hznt4w0 p{
                            display: flex;
                            justify-self: center;
                            padding-left: 140px;
                        }
                    }
                    </style>
                """, unsafe_allow_html=True)
    image_path = "images/img-bee-movie.jpg"
    with st.container(horizontal_alignment='center'):
        st.title('Quiz finalizado!! Parabéns!!', width='content')
        if pontuacao >= 8:
            st.balloons()
            st.markdown(f"## Pontuação :green[{pontuacao}/10]", width='content')
            st.markdown("##### 🔥 Mandou muito bem! Você dominou o quiz e mostrou que tá por dentro do assunto!", width='content')
            st.image(image_path, caption='Parabéns!', width=715)
        elif pontuacao >= 4:
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

def jogar_quiz(tema, perguntas, pagina):
    st.markdown("""
                <style>
                .block-container {
                    padding-top: 1.6rem; 
                    padding-bottom: 1rem;
                }
                .stButton > button {
                    font-size: 1.5rem; 
                }
                </style>
            """, unsafe_allow_html=True)
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
            
        if st.session_state.quiz_iniciado :
            st.set_page_config(page_title='Perguntas | Bee Smart', page_icon='🐝', layout='wide')
            st.markdown("""
                    <style>
                    .block-container {
                        padding-top: 1.6rem; 
                        padding-bottom: 1rem;
                    }
                    .st-emotion-cache-tn0cau{
                        gap:0px
                    }
                    @media (max-width: 700px){
                        .st-emotion-cache-tn0cau{
                            font-size: 0.5rem
                        }
                    }
                    </style>
                """, unsafe_allow_html=True)

            titulo = json_perguntas['titulo']
            
            st.markdown('## ' + titulo)
            with st.container(border=True, horizontal_alignment='center'):
                st.markdown(f'### Pergunta {st.session_state.numero_pergunta + 1}/10')
                
                pergunta_atual = json_perguntas['perguntas'][st.session_state.numero_pergunta]['pergunta']
                st.markdown('#### ' + pergunta_atual)
                
                respostas_validas = []
                for index, resposta in enumerate(json_perguntas['perguntas'][st.session_state.numero_pergunta]['respostas']):
                    respostas_validas.append((index, resposta))
                        
                for index, resposta in respostas_validas:
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
                    
                    resposta_correta = json_perguntas['perguntas'][st.session_state.numero_pergunta]['resposta_correta']

    
                    if resposta == resposta_correta:
                        st.success(
                                f"🎉 Parabéns!!! Você acertou!\n\n"
                                f"💡 Explicação: {json_perguntas['perguntas'][st.session_state.numero_pergunta]['explicações'][index]}"
                        )
                    else:
                        st.error(
                            f"❌ Ops! Resposta errada.\n\n"
                            f"✅ A resposta certa era **{resposta_correta}**.\n\n"
                            f"💡 Explicação: {json_perguntas['perguntas'][st.session_state.numero_pergunta]['explicações'][index]}"
                        )  
                        
                    if st.session_state.respondeu_pergunta != False and st.session_state.numero_pergunta <= 8:
                        if st.button(label='Próxima Pergunta', key=f'pergunta_{st.session_state.numero_pergunta}'):
                            st.session_state.respondeu_pergunta = False
                            st.session_state.numero_pergunta += 1
                            st.rerun()
                    elif st.session_state.respondeu_pergunta != False and st.session_state.numero_pergunta == 9:
                        if st.button(label='Terminar quiz', key=f'btn_terminar_quiz_{st.session_state.numero_pergunta}'):
                            supabase.table('quiz').insert(
                            {
                                'pontuacao' : st.session_state.pontuacao,
                                'tema' : tema if re.match(r"^[\w\sÀ-ÿ\-\.,;:!?()]+$", tema) else "Tema inválido",
                                'tema_favoritado': False,
                                'data_quiz' : datetime.now().isoformat(),
                                'usuario_id' : st.session_state["user"].id
                            }).execute()             
                            
                            st.session_state.quiz_iniciado = False
                            st.session_state.numero_pergunta = 0
                            st.session_state.respondeu_pergunta = False
                            st.session_state.index_resposta_respondida = 0
                            st.rerun()
        else:    
            final_quiz(st.session_state.pontuacao)

            
def iniciar_quiz():
    st.set_page_config(page_title='Quiz | Bee Smart', page_icon='🐝', layout='wide')
    temas = [item['tema'] for item in supabase.table('quiz').select('tema').eq('usuario_id', st.session_state["user"].id).order(column='tema',desc=True).execute().data]
    st.markdown("""
                    <style>
                    .block-container {
                        padding-top: 1.6rem; 
                        padding-bottom: 1rem;
                          text-align: center;
                    }
                    .st-emotion-cache-wfksaw{
                        display:0;
                        gap:0;
                    }
                    </style>
                """, unsafe_allow_html=True)
    
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
            col_regra1, col_regra2, col_regra3 = st.columns([1,1,1])
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
            temas_anteriores = st.pills('Temas anteriores', temas[:3], selection_mode='single', label_visibility='collapsed')
            tema_selecionado = tema_input.strip() if tema_input.strip() else (temas_anteriores if temas_anteriores else None)
            
            if st.session_state.tema_escolhido == None and tema_selecionado:
                if not re.match(r"^[\w\sÀ-ÿ\-\.,;:!?()]+$", tema_selecionado):
                    st.error("⚠ Tema inválido! Use apenas letras, números e sinais básicos de pontuação.")
                else:
                    st.session_state.tema_escolhido = tema_selecionado
                    st.rerun()

            if st.session_state.tema_escolhido != None:
                with st.spinner(text=f'Aguarde a IA gerar suas perguntas sobre o tema {st.session_state.tema_escolhido}...'):
                    st.session_state.perguntas = gerar_perguntas(st.session_state.tema_escolhido)
                    if st.session_state.perguntas != None:
                        st.session_state.pagina_atual = 'quiz'
                        st.rerun()
                                                     
    elif st.session_state.pagina_atual == 'quiz':
        jogar_quiz(st.session_state.tema_escolhido, st.session_state.perguntas, st.session_state.pagina_atual)


if __name__ == '__main__':
    st.set_page_config(page_title="Bee Smart", layout="wide")

    st.markdown("""
        <style>
        .botao-topo {
            margin-top: 1.5rem; 
        }
        </style>
    """, unsafe_allow_html=True)

    menu_col1, menu_col2, menu_col3 = st.columns([1,1,0.2])
    
    with menu_col1:
        pagina_menu = st.radio(
            "Menu",
            ["Quiz", "Dashboard"],
            horizontal=True
        )

    with menu_col1:
        st.markdown('<div class="botao-topo">', unsafe_allow_html=True)
        if 'user' in st.session_state:
            if st.button("❌ Sair"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state['pagina_atual'] = 'login'
                st.rerun()
        elif st.session_state.get('pagina_atual') == "cadastro":
            if st.button("🔙 Voltar"):
                st.session_state['pagina_atual'] = 'login'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if pagina_menu == "Quiz":
        if 'user' not in st.session_state:
            if st.session_state.get('pagina_atual') == "cadastro":
                tela_cadastro()
            else:
                tela_login()
        else:
            iniciar_quiz()

    elif pagina_menu == "Dashboard":
        if 'user' not in st.session_state:
            st.warning("Faça login para acessar o Dashboard")
        else:
            with st.spinner("Carregando dashboard, aguarde..."):
                dashboard.main()
