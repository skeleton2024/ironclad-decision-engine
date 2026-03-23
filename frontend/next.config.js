/** @type {import('next').NextConfig} */
const nextConfig = {
  // 反向代理到 FastAPI
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
