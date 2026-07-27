import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Use · Orqivium',
  description: 'Terms governing access to and use of Orqivium.',
}

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-background-body px-6 py-16 text-text-primary">
      <article className="mx-auto max-w-3xl rounded-2xl border border-divider-subtle bg-background-default p-8 shadow-xs sm:p-12">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-text-accent">Orqivium</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Terms of Use</h1>
        <p className="mt-4 text-sm text-text-tertiary">Effective: July 27, 2026</p>

        <div className="mt-10 space-y-8 text-base leading-7 text-text-secondary">
          <section>
            <h2 className="text-xl font-semibold text-text-primary">1. Scope</h2>
            <p className="mt-2">These terms govern access to Orqivium software, hosted services, interfaces, APIs, command-line tools, and related documentation made available by the project operator.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">2. Authorized use</h2>
            <p className="mt-2">You may use Orqivium only for lawful purposes and within the permissions, licenses, organizational policies, and technical limits that apply to your deployment. You are responsible for workflows, models, data, tools, credentials, and actions configured through the platform.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">3. AI and automation</h2>
            <p className="mt-2">AI-generated outputs and autonomous actions can be incomplete or incorrect. High-impact decisions require appropriate human review, testing, authorization, monitoring, and fallback procedures. Governance reports reduce risk but do not guarantee safety, legality, accuracy, or fitness for a particular purpose.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">4. Security</h2>
            <p className="mt-2">You must protect account credentials and secrets, configure least-privilege access, keep dependencies current, and report suspected vulnerabilities responsibly. Do not attempt unauthorized access, disruption, abuse, or circumvention of safeguards.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">5. Ownership and licenses</h2>
            <p className="mt-2">Orqivium-specific branding, architecture, governance extensions, documentation, and release materials are maintained by Kamran Ullah Afaq. Third-party components remain governed by their respective licenses and notices.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-text-primary">6. Changes</h2>
            <p className="mt-2">These terms may be updated as the product, deployment model, and applicable requirements evolve. The effective date above identifies the current published version.</p>
          </section>
        </div>

        <p className="mt-12 border-t border-divider-subtle pt-6 text-sm text-text-tertiary">Project operator: Kamran Ullah Afaq · X/Twitter: @kamranullahafaq</p>
      </article>
    </main>
  )
}
