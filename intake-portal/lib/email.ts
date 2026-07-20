// Stuurt een melding via Resend zodra een klant een formulier invult.
// Faalt stil: een mail-probleem mag de inzending nooit blokkeren.
export async function notifyNewResponse(formTitle: string, formId: string) {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.NOTIFY_EMAIL;
  const from = process.env.RESEND_FROM || "onboarding@resend.dev";
  if (!key || !to) return; // niet geconfigureerd = overslaan

  const appUrl = process.env.NEXT_PUBLIC_APP_URL || "";
  const link = appUrl ? `${appUrl}/responses/${formId}` : `/responses/${formId}`;

  try {
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: `Efficienter Intake <${from}>`,
        to: [to],
        subject: `Nieuwe inzending: ${formTitle}`,
        html: `<p>Er is een nieuw formulier ingevuld: <strong>${formTitle}</strong>.</p>
               <p><a href="${link}">Bekijk de antwoorden</a></p>`,
      }),
    });
  } catch {
    // stil falen
  }
}
