docker system prune -a
# docker build -t my_python_app .
docker build -t my_flask_app .

docker run -p 5000:5000 my_flask_app

# docker run -p 5000:5000 my_python_app
# docker run -it --cpus="4" --memory="8g" -p 5000:5000 my_python_app
# docker run -it --rm my_python_app /bin/sh
# rm -rf /var/lib/apt/lists/*