import type { ComponentType, ReactNode } from 'react';
import { motion, type MotionProps } from 'framer-motion';
import type { LucideProps } from 'lucide-react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

type IconComponent = ComponentType<LucideProps>;

export const fadeUp = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0 },
};

export const staggerContainer = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.08,
    },
  },
};

export function PageFrame({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <section className={cn('relative h-full overflow-y-auto overflow-x-hidden custom-scrollbar', className)}>
      <div className="pointer-events-none fixed inset-0 premium-grid opacity-70" aria-hidden="true" />
      <div className="pointer-events-none fixed -right-24 top-12 h-72 w-72 rounded-full bg-blue-500 orb" aria-hidden="true" />
      <div className="pointer-events-none fixed bottom-0 left-1/3 h-80 w-80 rounded-full bg-cyan-400 orb" aria-hidden="true" />
      <div className="relative z-10">{children}</div>
    </section>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  icon: Icon,
  action,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  icon?: IconComponent;
  action?: ReactNode;
}) {
  return (
    <motion.header
      variants={fadeUp}
      initial="hidden"
      animate="show"
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"
    >
      <div className="max-w-3xl">
        {eyebrow ? (
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.28em] text-blue-300">{eyebrow}</p>
        ) : null}
        <div className="flex items-center gap-3">
          {Icon ? (
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-blue-400/20 bg-blue-500/10 text-blue-300">
              <Icon className="h-5 w-5" aria-hidden="true" />
            </div>
          ) : null}
          <h1 className="text-3xl font-semibold tracking-tight text-white md:text-5xl">{title}</h1>
        </div>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 md:text-base">{description}</p>
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </motion.header>
  );
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
  tone = 'blue',
  trend,
}: {
  icon: IconComponent;
  label: string;
  value: string | number;
  detail: string;
  tone?: 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red';
  trend?: string;
}) {
  const tones = {
    blue: 'from-blue-500/18 text-blue-200 ring-blue-400/20',
    green: 'from-emerald-500/18 text-emerald-200 ring-emerald-400/20',
    orange: 'from-orange-500/18 text-orange-200 ring-orange-400/20',
    purple: 'from-violet-500/18 text-violet-200 ring-violet-400/20',
    cyan: 'from-cyan-500/18 text-cyan-200 ring-cyan-400/20',
    red: 'from-red-500/18 text-red-200 ring-red-400/20',
  };

  return (
    <motion.article
      variants={fadeUp}
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="glass group rounded-3xl p-5 ring-1 ring-white/5"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">{label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">{value}</p>
          <p className="mt-2 text-sm leading-6 text-slate-300">{detail}</p>
        </div>
        <div className={cn('rounded-2xl bg-gradient-to-br to-white/5 p-3 ring-1', tones[tone])}>
          <Icon className="h-5 w-5" aria-hidden="true" />
        </div>
      </div>
      {trend ? (
        <div className="mt-5 inline-flex rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-slate-200">
          {trend}
        </div>
      ) : null}
    </motion.article>
  );
}

export function Panel({
  children,
  className,
  motionProps,
}: {
  children: ReactNode;
  className?: string;
  motionProps?: MotionProps;
}) {
  return (
    <motion.div
      variants={fadeUp}
      transition={{ duration: 0.42, ease: 'easeOut' }}
      className={cn('glass rounded-3xl ring-1 ring-white/5', className)}
      {...motionProps}
    >
      {children}
    </motion.div>
  );
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-2xl bg-white/[0.07]', className)} aria-hidden="true" />;
}

export function LoadingState({ label = 'Loading operations data...' }: { label?: string }) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center gap-3 rounded-3xl border border-white/10 bg-white/[0.03] p-8 text-center">
      <Loader2 className="h-6 w-6 animate-spin text-blue-300" aria-hidden="true" />
      <p className="text-sm font-medium text-slate-300">{label}</p>
    </div>
  );
}

export function EmptyState({
  icon: Icon = AlertTriangle,
  title,
  description,
  action,
}: {
  icon?: IconComponent;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center rounded-3xl border border-dashed border-white/15 bg-white/[0.03] p-8 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/[0.06] text-slate-300">
        <Icon className="h-6 w-6" aria-hidden="true" />
      </div>
      <h2 className="text-lg font-semibold text-white">{title}</h2>
      <p className="mt-2 max-w-sm text-sm leading-6 text-slate-400">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-red-400/20 bg-red-500/10 p-4 text-sm text-red-100" role="alert">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <p>{message}</p>
      </div>
    </div>
  );
}
