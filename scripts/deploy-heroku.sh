
#!/bin/bash
echo "🟣 Deploying to Heroku..."

if ! command -v heroku &> /dev/null; then
    echo "❌ Please install Heroku CLI first:"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "Please login to Heroku..."
heroku login

APP_NAME=${1:-"url-shortener-$(date +%s)"}
echo "Creating Heroku app: $APP_NAME"
heroku create $APP_NAME

heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -hex 32) --app $APP_NAME

if [ ! -d "../.git" ]; then
    cd ..
    git init
    git add .
    git commit -m "Initial commit"
    cd scripts
fi

cd ..
heroku git:remote -a $APP_NAME

echo "🚀 Deploying to Heroku..."
git push heroku main

echo "✅ Deployed to Heroku!"
echo "🌐 Your app is available at: https://$APP_NAME.herokuapp.com"
EOF

chmod +x deploy-heroku.sh