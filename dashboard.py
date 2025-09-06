import streamlit as st
from app import supabase
from urllib.parse import quote
import pandas as pd
import altair as alt


def pegar_dados_geral_quiz():
    return  supabase.table('quiz').select('pontuacao, usuario(nome), usuario_id, data_quiz').execute().data

def pegar_dados_geral_usuarios():
    dados_geral_usuarios = supabase.table('usuario').select('*').execute()
    total_jogadores = len(dados_geral_usuarios.data) 
    
    return total_jogadores

def pegar_dados_usuario():
    dados = supabase.table('quiz').select('*').eq('usuario_id', st.session_state["user"].id).execute()
    
    perguntas_totais = len(dados.data)
    pontuacao_total = 0
    for pergunta in dados.data:
        pontuacao_total += pergunta['pontuacao']
        
    return perguntas_totais, pontuacao_total

def pegar_grafico_linha():
    dados = pegar_dados_geral_quiz()

    pontuacao_data = []

    for usuario in dados:
        if usuario["usuario_id"] == st.session_state["user"].id: 
            pontuacao_data.append({
                'data' : pd.to_datetime(usuario['data_quiz']),
                'pontuacao' : usuario['pontuacao']
            })

    if pontuacao_data:
        df = pd.DataFrame(pontuacao_data)
        df.set_index("data", inplace=True)
    else:
        df = pd.DataFrame(columns=['data','pontuacao']).set_index('data')
    
    return df.sort_values('data')
    

def pegar_ranking():
    dados = pegar_dados_geral_quiz()
    
    ranking = []
    ids_adicionados = set()
    
    for usuario in dados:
        uid = usuario['usuario_id']
        if uid not in ids_adicionados:
            ids_adicionados.add(uid)
            ranking.append(
                {
                    'usuario_id': usuario['usuario_id'],
                    'pontuacao_total' : usuario['pontuacao'],
                    'nome' : usuario['usuario']['nome']
                }
            )
        else:
            for r in ranking:
                if(r['usuario_id'] == uid):
                    r['pontuacao_total'] += usuario['pontuacao']
                    break
    
    
    return ranking

def main():
    st.markdown("""
                    <style>
                    .block-container {
                        padding-top: 1.6rem; 
                        padding-bottom: 1rem;
                    }
                    </style>
                """, unsafe_allow_html=True)
    total_jogadores = pegar_dados_geral_usuarios()
    partidas_totais, pontuacao_total = pegar_dados_usuario()
    st.set_page_config(page_title='Dashboard | Quiz', layout='wide')
    
    with st.container():
        cl_metrica1, cl_metrica2, cl_metrica3 = st.columns(3, border=True)
        
        with cl_metrica1:
            st.metric(label='Total de Jogadores', value=total_jogadores)
        
        with cl_metrica2:
            st.metric(label='Total de partidas jogadas por você', value=partidas_totais)
        
        with cl_metrica3:
            st.metric(label='Sua Pontuação Total', value=pontuacao_total)
            
        col_ranking, col_grafico= st.columns([1, 2], border=True)
        
 
        with col_ranking:
            st.subheader("🏆 Ranking Bee Smart")
            
            lista = pegar_ranking()
            
            lista_ranking = sorted(lista, key=lambda x: x['pontuacao_total'], reverse=True) 
           
            
            col_ranking, col_nome, col_pontuacao = st.columns([1,1.8,1])
            
            with col_ranking:
                st.markdown('###### Ranking')
            with col_nome:
                st.markdown('###### Nome')
            with col_pontuacao:
                st.markdown('###### Pontuação')
            
            for index, usuario in enumerate(lista_ranking):
                                
                if index <= 4 and not usuario["usuario_id"] == st.session_state["user"].id: 
                    with col_ranking:
                        st.markdown('##### ' + str(index+1) + '°')
                    with col_nome:
                        st.markdown('#### **' + usuario['nome'] + '**')
                    with col_pontuacao:
                        st.markdown('##### **' + str(usuario['pontuacao_total']) + '**')
                elif  index <= 4 and usuario["usuario_id"] == st.session_state["user"].id:
                    with col_ranking:
                        st.markdown('##### ' + str(index+1) + '°')
                    with col_nome:
                        st.markdown('##### **:red[VOCÊ]**')
                    with col_pontuacao:
                        st.markdown('##### **' + str(usuario['pontuacao_total']) + '**')
                elif index >= 5 and usuario["usuario_id"] == st.session_state["user"].id: 
                    with col_ranking:
                        st.markdown(f'##### {index+1}°')
                    with col_nome:
                        st.markdown('##### **:red[VOCÊ]**')
                    with col_pontuacao:
                        st.markdown('##### **' + str(usuario['pontuacao_total']) + '**')
                        
        with col_grafico:
            df = pegar_grafico_linha()

            if df.empty:
                st.info("Ainda não há dados de quiz para exibir.")
            else:
                st.line_chart(df, x_label='Data', y_label='Pontuação', use_container_width=True)
