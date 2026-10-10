import { cx } from '../lib/utils'

type Anim = 'float' | 'bounce' | 'wiggle' | 'pulse' | 'sparkle'

/** Decorative animated emoji. Hidden from assistive tech; meaning is carried by adjacent text. */
export function Emoji({ symbol, anim = 'float', size = 24, delay = 0, className }: { symbol: string; anim?: Anim; size?: number; delay?: number; className?: string }) {
  return (
    <span aria-hidden="true" className={cx('emoji', `emoji-${anim}`, className)} style={{ fontSize: size, animationDelay: `${delay}s` }}>
      {symbol}
    </span>
  )
}
