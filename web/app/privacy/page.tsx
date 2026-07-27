import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Notice · Orqivium',
  description: 'Privacy information for Orqivium deployments.',
}

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-background-body px-6 py-16 text-text-primary">
      <article className="mx-auto max-w-3xl rounded-2xl border border-divider-subtle bg-background-default p-8 shadow-xs sm:p-12">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-text-accent">Orqivium</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Privacy Notice</h1>
        <p className="mt-4 text-sm text-text-tertiary">Effective: July 27, 2026</p>

        <div className="mt-10 space-y-8 text-base leading-7 text-text-secondary">
          <section>
            <h2 className="text-xl font-semibold text-text-primary">1. Deployment responsibility</h2>
            <p className="mt-2">Orqivium can be self-hosted or operated as part of a private environment. The organization operating a deployment determines which data is collected, why it is processed, where it is stored, retention periods, and who can access it.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">2. Data the platform may process</h2>
            <p className="mt-2">Depending on configuration, the platform may process account information, prompts, uploaded files, knowledge-base content, model inputs and outputs, workflow definitions, tool requests, execution traces, audit findings, logs, and operational telemetry.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">3. External providers</h2>
            <p className="mt-2">Models, storage systems, vector databases, observability services, plugins, MCP servers, and other connected tools may receive data according to deployment configuration. Operators should review each provider, minimize transmitted data, and establish appropriate agreements and controls.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">4. Security and retention</h2>
            <p className="mt-2">Operators should use encryption, least-privilege access, secret management, network controls, backups, retention limits, incident response, and deletion procedures suitable for the sensitivity and jurisdiction of the data.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">5. Your choices</h2>
            <p className="mt-2">Requests to access, correct, export, restrict, or delete data should be directed to the organization operating the relevant Orqivium deployment. Self-hosted operators are responsible for publishing deployment-specific privacy information.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">6. Product telemetry</h2>
            <p className="mt-2">Optional analytics and error reporting should be disabled or configured where they are not appropriate. Deployment owners should document enabled telemetry and avoid sending confidential content unless explicitly authorized.</p>
          </section>
        </div>

        <p className="mt-12 border-t border-divider-subtle pt-6 text-sm text-text-tertiary">Project operator: Kamran Ullah Afaq · X/Twitter: @kamranullahafaq</p>
      </article>
    </main>
  )
}
