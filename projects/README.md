# Projects

One folder per job. Create one with `/new-video-brief <slug>` (video jobs) or by copying a
squad's brief template.

```
projects/<slug>/
  brief.md      what to make, inputs, constraints, credit cap   (committed)
  assets/       voiceover/ footage/ brand/ music/                (gitignored)
  work/         everything the squad produces on the way        (gitignored)
  output/       deliverables                                     (gitignored)
```

Media never goes in git. In a cloud session, list download URLs in the brief instead.
