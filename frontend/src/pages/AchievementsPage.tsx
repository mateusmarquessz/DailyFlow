import { useQuery } from '@tanstack/react-query'
import { Flame, Lock, Trophy, Zap } from 'lucide-react'

import { gamificationApi } from '@/api/gamification'
import { getAchievementIcon } from '@/components/achievements/achievementIcons'
import { Alert } from '@/components/ui/Alert'
import { Card } from '@/components/ui/Card'
import type { AchievementCatalogEntry } from '@/types/gamification'

function formatUnlockedAt(value: string | null): string | null {
  if (!value) return null
  const [year, month, day] = value.slice(0, 10).split('-')
  return `${day}/${month}/${year}`
}

function AchievementCard({ achievement }: { achievement: AchievementCatalogEntry }) {
  const Icon = getAchievementIcon(achievement.icon)
  const unlockedAt = formatUnlockedAt(achievement.unlocked_at)

  return (
    <Card
      className={`flex items-start gap-3 p-4 transition-opacity ${
        achievement.unlocked ? '' : 'opacity-60 grayscale'
      }`}
    >
      <div
        className={`flex size-11 shrink-0 items-center justify-center rounded-xl ${
          achievement.unlocked
            ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300'
            : 'bg-surface-100 text-surface-400 dark:bg-surface-800 dark:text-surface-500'
        }`}
      >
        {achievement.unlocked ? <Icon className="size-5" /> : <Lock className="size-5" />}
      </div>
      <div className="min-w-0">
        <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{achievement.title}</p>
        <p className="mt-0.5 text-sm text-surface-500 dark:text-surface-400">{achievement.description}</p>
        {unlockedAt && (
          <p className="mt-1 text-xs text-brand-600 dark:text-brand-300">Desbloqueada em {unlockedAt}</p>
        )}
      </div>
    </Card>
  )
}

export function AchievementsPage() {
  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['gamification-profile'],
    queryFn: () => gamificationApi.profile(),
  })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Conquistas</h1>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          Acompanhe seu nível, sua sequência e desbloqueie medalhas conforme avança na sua rotina.
        </p>
      </div>

      {isLoading && <p className="text-sm text-surface-500 dark:text-surface-400">Carregando seu progresso…</p>}

      {isError && <Alert variant="error">Não foi possível carregar suas conquistas. Tente novamente.</Alert>}

      {profile && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Card className="flex items-center gap-4 p-5">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300">
                <Zap className="size-6" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-surface-500 dark:text-surface-400">Nível {profile.level}</p>
                <p className="text-lg font-semibold text-surface-900 dark:text-surface-50">{profile.xp_total} XP</p>
                <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-surface-100 dark:bg-surface-800">
                  <div
                    className="h-full rounded-full bg-brand-600 transition-all"
                    style={{ width: `${Math.min(100, Math.max(0, profile.level_progress_percent))}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-surface-500 dark:text-surface-400">
                  Faltam {Math.max(0, profile.xp_for_next_level - profile.xp_total)} XP para o próximo nível
                </p>
              </div>
            </Card>

            <Card className="flex items-center gap-4 p-5">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-300">
                <Flame className="size-6" />
              </div>
              <div>
                <p className="text-xs text-surface-500 dark:text-surface-400">Sequência atual</p>
                <p className="text-lg font-semibold text-surface-900 dark:text-surface-50">
                  {profile.current_streak} {profile.current_streak === 1 ? 'dia' : 'dias'}
                </p>
              </div>
            </Card>

            <Card className="flex items-center gap-4 p-5">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-300">
                <Trophy className="size-6" />
              </div>
              <div>
                <p className="text-xs text-surface-500 dark:text-surface-400">Maior sequência</p>
                <p className="text-lg font-semibold text-surface-900 dark:text-surface-50">
                  {profile.longest_streak} {profile.longest_streak === 1 ? 'dia' : 'dias'}
                </p>
              </div>
            </Card>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Galeria de medalhas</h2>
            <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
              {profile.achievements.filter((achievement) => achievement.unlocked).length} de {profile.achievements.length}{' '}
              desbloqueadas
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {profile.achievements.map((achievement) => (
                <AchievementCard key={achievement.code} achievement={achievement} />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
