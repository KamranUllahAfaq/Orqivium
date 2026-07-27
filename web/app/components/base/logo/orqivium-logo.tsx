'use client'
import type { FC } from 'react'
import { cn } from '@orqivium/ui/cn'
import useTheme from '@/hooks/use-theme'
import { basePath } from '@/utils/var'

export type LogoStyle = 'default' | 'monochromeWhite'

export const logoPathMap: Record<LogoStyle, string> = {
  default: '/logo/logo.svg',
  monochromeWhite: '/logo/logo-monochrome-white.svg',
}

export type LogoSize = 'large' | 'medium' | 'small'

export const logoSizeMap: Record<LogoSize, string> = {
  large: 'w-[154px] h-9',
  medium: 'w-[128px] h-7',
  small: 'w-[96px] h-[22px]',
}

type OrqiviumLogoProps = {
  style?: LogoStyle
  size?: LogoSize
  className?: string
  alt?: string
}

const OrqiviumLogo: FC<OrqiviumLogoProps> = ({
  style = 'default',
  size = 'medium',
  className,
  alt = 'Orqivium',
}) => {
  const { theme } = useTheme()
  const themedStyle = theme === 'dark' && style === 'default' ? 'monochromeWhite' : style

  return (
    <img
      src={`${basePath}${logoPathMap[themedStyle]}`}
      className={cn('block object-contain', logoSizeMap[size], className)}
      alt={alt}
    />
  )
}

export default OrqiviumLogo
