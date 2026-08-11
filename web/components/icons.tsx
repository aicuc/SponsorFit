import type { SVGProps } from "react";

export function ArrowIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true" {...props}>
      <path d="M4 10h11M10.5 4.5 16 10l-5.5 5.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

export function GithubIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" {...props}>
      <path
        fill="currentColor"
        d="M12 .7A11.5 11.5 0 0 0 8.36 23.1c.58.1.79-.25.79-.56v-2.2c-3.24.7-3.92-1.38-3.92-1.38-.52-1.35-1.29-1.7-1.29-1.7-1.06-.73.08-.72.08-.72 1.17.09 1.79 1.2 1.79 1.2 1.04 1.8 2.73 1.28 3.4.98.1-.76.4-1.28.74-1.57-2.59-.3-5.31-1.3-5.31-5.69 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.47.11-3.05 0 0 .97-.31 3.16 1.18A10.9 10.9 0 0 1 12 6.11c.98 0 1.95.13 2.86.39 2.2-1.49 3.16-1.18 3.16-1.18.63 1.58.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.4-2.73 5.38-5.33 5.67.42.37.79 1.09.79 2.19v3.22c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .7Z"
      />
    </svg>
  );
}

export function SparkIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" {...props}>
      <path d="M12 1.8c.35 5.96 3.74 9.35 9.7 9.7-5.96.35-9.35 3.74-9.7 9.7-.35-5.96-3.74-9.35-9.7-9.7 5.96-.35 9.35-3.74 9.7-9.7Z" fill="currentColor" />
    </svg>
  );
}

export function CopyIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true" {...props}>
      <rect x="6" y="6" width="10" height="10" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <path d="M13.5 6V4.5A1.5 1.5 0 0 0 12 3H4.5A1.5 1.5 0 0 0 3 4.5V12a1.5 1.5 0 0 0 1.5 1.5H6" fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}
