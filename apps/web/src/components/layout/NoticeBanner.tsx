type NoticeBannerProps = {
  notice: string;
};

export function NoticeBanner({ notice }: NoticeBannerProps) {
  return (
    <section className="notice" role="status" aria-live="polite">
      {notice}
    </section>
  );
}
