import {
  BookOpen,
  Brain,
  CheckCircle2,
  Coffee,
  Dumbbell,
  Droplet,
  Heart,
  Moon,
  Music,
  Sun,
  type LucideIcon,
} from 'lucide-react'

export const HABIT_ICONS: Record<string, LucideIcon> = {
  'check-circle': CheckCircle2,
  droplet: Droplet,
  'book-open': BookOpen,
  dumbbell: Dumbbell,
  moon: Moon,
  sun: Sun,
  heart: Heart,
  brain: Brain,
  coffee: Coffee,
  music: Music,
}

export const HABIT_ICON_OPTIONS = Object.keys(HABIT_ICONS) as (keyof typeof HABIT_ICONS)[]

export function getHabitIcon(name: string): LucideIcon {
  return HABIT_ICONS[name] ?? CheckCircle2
}
