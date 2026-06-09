import {
  CheckCircle2,
  Crown,
  Flame,
  ListChecks,
  Rocket,
  Sparkles,
  Star,
  Target,
  Trophy,
  type LucideIcon,
} from 'lucide-react'

export const ACHIEVEMENT_ICONS: Record<string, LucideIcon> = {
  'check-circle-2': CheckCircle2,
  'list-checks': ListChecks,
  rocket: Rocket,
  crown: Crown,
  sparkles: Sparkles,
  flame: Flame,
  star: Star,
  trophy: Trophy,
  target: Target,
}

export function getAchievementIcon(name: string): LucideIcon {
  return ACHIEVEMENT_ICONS[name] ?? Trophy
}
