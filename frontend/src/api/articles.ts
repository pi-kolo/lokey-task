import _ from 'lodash';
import { Article } from 'src/model/Article';
import getCrudifulAxios from './axios_config';

export async function getArticles(): Promise<Article[]> {
    const path = 'articles';
    const response = await getCrudifulAxios().get(path);
    response.data.forEach((article: Article, i: number, list: Article[]) => {
      list[i] = <Article><unknown>_.mapKeys(article as object, (v: object, k: string) => _.camelCase(k));
      list[i].releaseDate = list[i].releaseDate && new Date(<Date>list[i].releaseDate);
    });
  
    return response.data;
  }
  
  export async function updateArticle(article: Article) {
    const path = `articles/${article.articleId}`;
    const request = {
      title: article.title,
      content: article.content,
      release_date: article.releaseDate,
    };
  
    return await getCrudifulAxios().put(path, request);
  }
  
  export async function deleteArticle(article: Article) {
    const path = `articles/${article.articleId}`;
    return await getCrudifulAxios().delete(path);
  }
  
  export async function addNewArticle(article: Article) {
    const path = 'articles';
    return await getCrudifulAxios().post(path, article);
  }
  