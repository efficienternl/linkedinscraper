import { NextRequest, NextResponse } from "next/server";

// Beschermt het admin-gedeelte met een wachtwoord (HTTP Basic Auth).
// De publieke invulpagina (/f/...) blijft vrij toegankelijk voor klanten.
export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Publiek: de invulpagina voor klanten
  if (pathname.startsWith("/f/")) return NextResponse.next();

  const user = process.env.ADMIN_USER || "efficienter";
  const pass = process.env.ADMIN_PASSWORD;

  // Geen wachtwoord ingesteld (bijv. lokaal) = niet beschermen
  if (!pass) return NextResponse.next();

  const auth = req.headers.get("authorization");
  if (auth) {
    const [scheme, encoded] = auth.split(" ");
    if (scheme === "Basic" && encoded) {
      const decoded = atob(encoded);
      const i = decoded.indexOf(":");
      const u = decoded.slice(0, i);
      const p = decoded.slice(i + 1);
      if (u === user && p === pass) return NextResponse.next();
    }
  }

  return new NextResponse("Authenticatie vereist", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Efficienter Intake Portal"' },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|logo.png).*)"],
};
