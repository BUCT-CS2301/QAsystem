# 阶段1：构建 Vue 项目（node 环境）
FROM node:latest as build-stage

# 设置工作目录
WORKDIR /app

ENV NODE_OPTIONS=--max-old-space-size=512
# 复制 Vue 项目代码
COPY vue/vue-project/ .

# 安装依赖并打包
RUN npm install --legacy-peer-deps --no-audit --no-fund
RUN npm run build

# 阶段2：生产环境（仅 Nginx）
FROM nginx:alpine as production-stage

# 复制打包好的 Vue  dist 到 Nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
