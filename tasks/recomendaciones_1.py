import pandas as pd


def recomendacion(peliculas, user, peliGenres):
 
    movies_df = pd.DataFrame(peliculas)


    movies_df_copy = pd.DataFrame(peliGenres)
    inputMovies = pd.DataFrame(user)

    movies_df = movies_df.drop('genres',1)
    #Filtrar las películas por título 
    inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]

    #Luego fusionándolo para que podamos obtener el movieId. Lo está fusionando implícitamente por título. 
    inputMovies = pd.merge(inputId, inputMovies)
    


    #Eliminar información que no usaremos del dataframe
    #inputMovies = inputMovies.drop('year', 1)
    #Final input dataframe
    #inputMovies
    #Filtrar a los usuarios que han visto películas que la entrada ha visto y almacenarlas 
    userSubset = movies_df_copy[movies_df_copy['imdb_id'].isin(inputMovies['imdb_id'].tolist())]



    userSubset = userSubset.reset_index(drop=True)
    tabla_generos = userSubset.drop("imdb_id",1).drop("title",1)
   
    perfil_usu = tabla_generos.transpose().dot(inputMovies['rating'])
   
    generos = movies_df_copy.set_index(movies_df_copy['imdb_id'])

    generos = generos.drop("imdb_id",1).drop("title",1)
   
    generos.shape

    recom = ((generos*perfil_usu).sum(axis=1))/(perfil_usu.sum())
    recom = recom.sort_values(ascending=False)
    #recommendation_df = movies_df.loc[movies_df['imdb_id'].isin(recom.head(20).keys())]

    #recommendation_df = recommendation_df.drop("year",1)


    #jsonTx = recommendation_df.to_json()
 
    return recom.head(24).keys().tolist()

    
    




