// Adaptateur commun en lecture seule. Pas d'identité de production ni de rendu dans le Worker.
import catalogue from '../../catalogue/catalogue.json' with {type:'json'};
export default {async fetch(req){const url=new URL(req.url);if(req.method!=='GET')return new Response('Méthode non permise',{status:405,headers:{Allow:'GET'}});if(url.pathname==='/v1/catalogue')return Response.json(catalogue);if(url.pathname==='/v1/health')return Response.json({mode:'reference',renderer:'github-actions',ota_implemented:false});return new Response('Introuvable',{status:404})}};
