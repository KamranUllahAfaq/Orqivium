import type { CommandEffect } from '@/framework/command'
import { OrqiviumCommand } from '@/commands/_shared/orqivium-command'
import { Flags } from '@/framework/flags'
import { realStreams } from '@/sys/io/streams'
import { enforceOrqiviumVersion } from '@/version/enforce'
import { agentGuide } from './guide'
import { runLogin } from './login'

export default class Login extends OrqiviumCommand {
  static override description = 'Sign in to Orqivium via OAuth device flow'

  static override effect: CommandEffect = 'write'

  static override examples = [
    '<%= config.bin %> auth login',
    '<%= config.bin %> auth login --host http://localhost',
    '<%= config.bin %> auth login --no-browser',
  ]

  static override flags = {
    host: Flags.string({
      description: 'Orqivium host URL',
      default: '',
    }),
    'no-browser': Flags.boolean({
      description: 'do not auto-open the browser',
      default: false,
    }),
    insecure: Flags.boolean({
      description: 'allow http:// hosts and skip TLS certificate verification (local-dev only)',
      default: false,
    }),
  }

  async run(argv: string[]): Promise<void> {
    const { flags } = this.parse(Login, argv)
    await runLogin({
      io: realStreams(),
      host: flags.host,
      noBrowser: flags['no-browser'],
      insecure: flags.insecure,
      verifyServer: async (host) => {
        await enforceOrqiviumVersion(host, { forceFresh: true, insecure: flags.insecure })
      },
    })
  }

  override agentGuide(): string {
    return agentGuide
  }
}
