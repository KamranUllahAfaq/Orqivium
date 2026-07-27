import { OrqiviumCommand } from '@/commands/_shared/orqivium-command'
import { Flags } from '@/framework/flags'
import { raw } from '@/framework/output'
import { runEnvList } from './run-list'

export default class EnvList extends OrqiviumCommand {
  static override description = 'Show every ORQIVIUM_* env var orqctl reads'

  static override examples = ['<%= config.bin %> env list', '<%= config.bin %> env list --json']

  static override flags = {
    json: Flags.boolean({ description: 'emit JSON', default: false }),
  }

  async run(argv: string[]) {
    const { flags } = this.parse(EnvList, argv)
    return raw(runEnvList({ json: flags.json }))
  }
}
