import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


def recomendacion(peliculas, user):
    movies_df = pd.DataFrame(peliculas)


    movies_df.head(10)

    #creamos una columna nueva que se llamará year
    movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
    #Quitando los paréntesis 
    movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
    #Eliminar los años de la columna "título" y el espacio
    movies_df['title'] = movies_df.title.str.replace(' (\(\d\d\d\d\))', '')
    movies_df['genres'] = movies_df.genres.str.split('|')



    movies_df.head(10)


    movies_df_copy = movies_df.copy()
    for index, row in movies_df.iterrows():
        for genre in row['genres']:
            movies_df_copy.at[index,genre] = 1

    movies_df_copy = movies_df_copy.fillna(0)
    inputMovies = pd.DataFrame(user)

    movies_df = movies_df.drop('genres',1)
    #Filtrar las películas por título 
    inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]
    #Luego fusionándolo para que podamos obtener el movieId. Lo está fusionando implícitamente por título. 
    inputMovies = pd.merge(inputId, inputMovies)
    #Eliminar información que no usaremos del dataframe
    inputMovies = inputMovies.drop('year', 1)
    #Final input dataframe
    inputMovies
    #Filtrar a los usuarios que han visto películas que la entrada ha visto y almacenarlas 
    userSubset = movies_df_copy[movies_df_copy['imdb_id'].isin(inputMovies['imdb_id'].tolist())]

    userSubset = userSubset.reset_index(drop=True)
    tabla_generos = userSubset.drop("imdb_id",1).drop("title",1).drop("genres",1).drop("year",1).drop("_id",1).drop("id",1).drop("original_language",1).drop("original_title",1).drop("overview",1).drop("popularity",1).drop("production_companies",1).drop("budget",1).drop("production_countries",1).drop("release_date",1).drop("revenue",1).drop("runtime",1).drop("spoken_languages",1).drop("status",1).drop("tagline",1).drop("vote_average",1).drop("vote_count",1).drop("production_companies_number",1).drop("production_countries_number",1).drop("spoken_languages_number",1)

    print(tabla_generos)
    userSubset.head(10)

    perfil_usu = tabla_generos.transpose().dot(inputMovies['rating'])
    generos = movies_df_copy.set_index(movies_df_copy['imdb_id'])

    generos = generos.drop("imdb_id",1).drop("title",1).drop("genres",1).drop("year",1)
    generos.shape

    recom = ((generos*perfil_usu).sum(axis=1))/(perfil_usu.sum())
  
    recom = recom.sort_values(ascending=False)

    recommendation_df = movies_df.loc[movies_df['imdb_id'].isin(recom.head(20).keys())]

    recommendation_df = recommendation_df.drop("year",1)
    recommendation_df.head(10)

    #jsonTx = recommendation_df.to_json()
    i = 0
    r = []
    for index, row in recommendation_df.iterrows():
        if i>11:
            break
        i += 1
        r.append(row)
    
    return r

    
    




