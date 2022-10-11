import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

movies_df = pd.read_csv('movies.csv')
ratings_df = pd.read_csv('ratings.csv')

movies_df.head(10)

#creamos una columna nueva que se llamará year
movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
#Quitando los paréntesis 
movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
#Eliminar los años de la columna "título" y el espacio
movies_df['title'] = movies_df.title.str.replace(' (\(\d\d\d\d\))', '')
movies_df['genres'] = movies_df.genres.str.split('|')

ratings_df = ratings_df.drop("timestamp",1)

movies_df.head(10)


movies_df_copy = movies_df.copy()
for index, row in movies_df.iterrows():
    for genre in row['genres']:
        movies_df_copy.at[index,genre] = 1

movies_df_copy = movies_df_copy.fillna(0)
movies_df_copy.head(10)

userInput = [
{'title':'Breakfast Club, The', 'rating':5},
{'title':'Toy Story', 'rating':3.5},
{'title':'Jumanji', 'rating':2},
{'title':'Pulp Fiction', 'rating':5},
{'title':'Akira', 'rating':4.5}
]
inputMovies = pd.DataFrame(userInput)
inputMovies.head(10)


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
userSubset = movies_df_copy[movies_df_copy['movieId'].isin(inputMovies['movieId'].tolist())]

userSubset = userSubset.reset_index(drop=True)
tabla_generos = userSubset.drop("movieId",1).drop("title",1).drop("genres",1).drop("year",1)


userSubset.head(10)

perfil_usu = tabla_generos.transpose().dot(inputMovies['rating'])


generos = movies_df_copy.set_index(movies_df_copy['movieId'])

generos = generos.drop("movieId",1).drop("title",1).drop("genres",1).drop("year",1)
generos.shape

perfil_usu.head(10)

recom = ((generos*perfil_usu).sum(axis=1))/(perfil_usu.sum())
recom.head()

recom = recom.sort_values(ascending=False)
recom.head(10)

recommendation_df = movies_df.loc[movies_df['movieId'].isin(recom.head(20).keys())]
recommendation_df_title = recommendation_df[['title']]

recommendation_df = recommendation_df.drop("year",1)
recommendation_df.head(10)

jsonTx = recommendation_df.to_json()
print(jsonTx)
    
    




