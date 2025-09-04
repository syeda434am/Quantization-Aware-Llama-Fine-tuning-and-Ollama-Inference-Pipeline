FROM ollama/ollama:latest

#WORKDIR /usr/share/ollama

#COPY Modelfile /usr/share/ollama/
#COPY model_file.gguf /usr/share/ollama/

RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    ollama create model -f /usr/share/ollama/Modelfile && \
    pkill ollama

EXPOSE 11434

CMD ["serve"]