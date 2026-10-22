# Rival humano: Maia (redes entrenadas con partidas reales de 1100 a 1900) sobre el motor lc0
FROM python:3.12-slim AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates curl g++ meson ninja-build pkg-config \
       libopenblas-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 -b v0.32.1 --recurse-submodules https://github.com/LeelaChessZero/lc0.git /lc0
WORKDIR /lc0
RUN ./build.sh -Dgtest=false
RUN mkdir /weights && for elo in 1100 1200 1300 1400 1500 1600 1700 1800 1900; do \
      curl -fsSL -o /weights/maia-$elo.pb.gz \
        https://raw.githubusercontent.com/CSSLab/maia-chess/master/maia_weights/maia-$elo.pb.gz; \
    done

FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libopenblas0 zlib1g libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /lc0/build/release/lc0 /usr/local/bin/lc0
COPY --from=build /weights /weights
RUN pip install --no-cache-dir fastapi==0.115.6 uvicorn==0.32.1 chess==1.11.1
COPY server.py /app/server.py
WORKDIR /app
ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
