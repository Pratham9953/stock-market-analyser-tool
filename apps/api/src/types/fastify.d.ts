import type { AuthContext } from '../modules/auth/session.service';

declare module 'fastify' {
  interface FastifyRequest {
    auth: AuthContext;
  }
}
