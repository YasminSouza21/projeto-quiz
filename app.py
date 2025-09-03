import streamlit as st
import time

def jogar_quiz(tema, pagina):
    if pagina == 'quiz':
        st.title(f'Quiz sobre {tema}', )

def iniciar_quiz():
    st.set_page_config(page_title='Quiz | Bee Smart', page_icon='🐝', layout='wide')
    
    if 'tema_escolhido' not in st.session_state:
        st.session_state.tema_escolhido = None
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = 'home'
    
    if st.session_state.pagina_atual == 'home':
        with st.container(vertical_alignment='center', horizontal_alignment='center'):
            st.markdown('# Seja bem-vindo ao Quiz :orange[Bee Smart] 🐝', width='content')
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
                    time.sleep(10)  
                    st.session_state.pagina_atual = 'quiz'
                    st.rerun()
                                                     
    elif st.session_state.pagina_atual == 'quiz':
        jogar_quiz(st.session_state.tema_escolhido, st.session_state.pagina_atual)
                

               
if __name__ == '__main__':
    iniciar_quiz()