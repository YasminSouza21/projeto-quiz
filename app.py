import streamlit as st
from google import genai
from dotenv import load_dotenv
import json
import os
import pandas as pd

load_dotenv()
api_key = os.getenv('API_KEY_GENAI')
genai_client = genai.Client(api_key=api_key)

def gerar_perguntas(tema): 
    response = genai_client.models.generate_content(
        model='gemini-1.5-flash',
        contents=f'Faça 5 perguntas sobre esse tema {tema}, cada pergunta deve conter 4 alternativas e suas respectivas explicações, me de em json a reposta do prompt, no json deve conter a chave chamada pergunta, uma chave chamada respostas e uma chave chamada explicações com as 4 alternativas sem nomear elas de A a B ou de 1 a 4 e a chave chamada resposta_correta dizendo qual resposta a correta, mas quero a resposta correta em texto da resposta, não o index que a resposta ta, e traz um titulo sobre o tema do quiz tipo Quiz sobre ai vem o nome do tema e depois um emoji a chave pode ter nome de titulo'
    ).to_json_dict() 
    return str(response['candidates'][0]['content']['parts'][0]['text']).replace('```', '').replace('json', '')

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
            
        if st.session_state.quiz_iniciado:
            st.set_page_config(layout='centered')
            st.title(json_perguntas['titulo'])
            with st.container(border=True, horizontal_alignment='center'):
                st.markdown(f'## Pergunta {st.session_state.numero_pergunta + 1}/5')
                st.markdown('### ' + json_perguntas['perguntas'][st.session_state.numero_pergunta]['pergunta'])
                for index,resposta in enumerate(json_perguntas['perguntas'][st.session_state.numero_pergunta]['respostas']):
                    if st.button(label=resposta, key=f'resposta_{index}', use_container_width=True, disabled=st.session_state.respondeu_pergunta):
                        st.session_state.resposta_respondida = resposta
                        st.session_state.respondeu_pergunta = True
                        st.session_state.index_resposta_respondida = index
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
                            st.rerun()
            
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
            st.markdown('### O Quiz que irá te ajudar a testar seus conhecimentos com qualquer **TEMA**!!!')
            col_regra1, col_regra2, col_regra3 = st.columns(3, border=True, vertical_alignment='center')
            with col_regra1:
                st.markdown('### Responda rápido e com atenção')
                st.markdown('Cada pergunta tem só uma alternativa correta. Leia com calma, mas não demore demais — o tempo passa voando, igual uma abelhinha ocupada. Concentrar é a chave para acertar mais.')
            with col_regra2:
                st.markdown('### Acertos valem pontos')
                st.markdown('Cada resposta correta soma pontos no seu placar. Quanto mais pontos, mais você prova que está realmente “bee smart”. Mas cuidado: respostas erradas não tiram pontos, só não ajudam você a subir no ranking.')
            with col_regra3:
                st.markdown('### Divirta-se aprendendo')
                st.markdown('O quiz não é só um desafio, é também uma chance de aprender coisas novas enquanto joga. Aproveite cada rodada para treinar sua mente, testar seu raciocínio e, claro, se divertir no processo.')
            
            st.markdown('#### ⇩ Insira abaixo o tema no qual você irá jogar ⇩', width='content')
            
            tema_input = st.text_input('', placeholder='Digite o tema aqui', label_visibility='collapsed') 
            temas_anteriores = st.pills('Temas anteriores', ['IA', 'Python', 'Java'], selection_mode='single', label_visibility='collapsed')
            tema_selecionado = tema_selecionado = tema_input.strip() if tema_input.strip() else (temas_anteriores if temas_anteriores else None)
            
            if st.session_state.tema_escolhido == None and tema_selecionado:
                st.session_state.tema_escolhido = tema_selecionado
                st.rerun()

            if st.session_state.tema_escolhido != None:
                with st.spinner(text=f'Aguarde a IA gerar suas perguntas sobre o tema {st.session_state.tema_escolhido}'):
                    st.session_state.perguntas = gerar_perguntas(st.session_state.tema_escolhido)
                    if st.session_state.perguntas != None:
                        st.session_state.pagina_atual = 'quiz'
                        st.rerun()
                                                     
    elif st.session_state.pagina_atual == 'quiz':
        jogar_quiz(st.session_state.perguntas, st.session_state.pagina_atual)
                

               
if __name__ == '__main__':
    iniciar_quiz()