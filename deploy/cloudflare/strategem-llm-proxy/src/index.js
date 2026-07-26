/**
 * OpenAI-compatible chat proxy over Cloudflare Workers AI.
 * Strategem operator BYOK points here (base_url + api_key = PROXY_SECRET).
 */
const DEFAULT_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function unauthorized() {
  return json({ error: { message: "unauthorized", type: "auth_error" } }, 401);
}

function checkAuth(request, env) {
  const secret = (env.PROXY_SECRET || "").trim();
  if (!secret) return false;
  const header = request.headers.get("authorization") || "";
  const m = header.match(/^Bearer\s+(.+)$/i);
  return Boolean(m && m[1].trim() === secret);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "GET" && (path === "/" || path === "/healthz")) {
      return json({ status: "ok", service: "strategem-llm-proxy" });
    }

    if (!checkAuth(request, env)) {
      return unauthorized();
    }

    if (request.method === "GET" && path === "/v1/models") {
      return json({
        object: "list",
        data: [
          {
            id: DEFAULT_MODEL,
            object: "model",
            owned_by: "cloudflare-workers-ai",
          },
        ],
      });
    }

    if (request.method === "POST" && path === "/v1/chat/completions") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: { message: "invalid json" } }, 400);
      }
      const model = String(body.model || DEFAULT_MODEL);
      const messages = body.messages;
      if (!Array.isArray(messages) || messages.length === 0) {
        return json({ error: { message: "messages required" } }, 400);
      }
      try {
        const result = await env.AI.run(model, {
          messages,
          max_tokens: body.max_tokens ?? 1024,
          temperature: body.temperature,
        });
        const content =
          typeof result === "string"
            ? result
            : result?.response ||
              result?.result?.response ||
              (Array.isArray(result?.choices)
                ? result.choices[0]?.message?.content
                : null) ||
              JSON.stringify(result);
        return json({
          id: `chatcmpl_${crypto.randomUUID()}`,
          object: "chat.completion",
          created: Math.floor(Date.now() / 1000),
          model,
          choices: [
            {
              index: 0,
              message: { role: "assistant", content: String(content ?? "") },
              finish_reason: "stop",
            },
          ],
        });
      } catch (err) {
        return json(
          {
            error: {
              message: err instanceof Error ? err.message : String(err),
              type: "workers_ai_error",
            },
          },
          502,
        );
      }
    }

    return json({ error: { message: `not found: ${path}` } }, 404);
  },
};
