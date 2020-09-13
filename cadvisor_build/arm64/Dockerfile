# Builder
FROM arm64v8/golang as builder

MAINTAINER Emil Schulz Østergaard <emil.ostergaard@gmail.com>

ENV CADVISOR_VERSION "v0.36.0"

RUN apt-get update && apt-get install -y git dmsetup && apt-get clean

RUN git clone --branch ${CADVISOR_VERSION} https://github.com/google/cadvisor.git /go/src/github.com/google/cadvisor

WORKDIR /go/src/github.com/google/cadvisor

RUN make build

# Image for usage
FROM arm64v8/debian

MAINTAINER Emil Schulz Østergaard <emil.ostergaard@gmail.com>

COPY --from=builder /go/src/github.com/google/cadvisor/cadvisor /usr/bin/cadvisor

EXPOSE 8080
ENTRYPOINT ["/usr/bin/cadvisor", "-logtostderr"]