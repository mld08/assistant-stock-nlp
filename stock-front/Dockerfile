# Étape 1 : Construction de l'application
FROM node:20-alpine as build-stage

WORKDIR /app

# Copier les fichiers package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code source
COPY . .

# Construire l'application
# On passe l'URL de l'API comme argument de build si nécessaire, 
# ou on la laisse être gérée par les variables d'environnement au runtime si supporté par le framework
RUN npm run build

# Étape 2 : Service des fichiers statiques avec Nginx
FROM nginx:stable-alpine as production-stage

# Copier la configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers buildés de l'étape précédente
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Exposer le port 80
EXPOSE 80

# Lancer Nginx
CMD ["nginx", "-g", "daemon off;"]
