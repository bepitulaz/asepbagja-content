import { z, defineCollection } from "astro:content";

const musicCollection = defineCollection({
  type: "data",
  schema: z.object({
    records: z.array(
      z.object({
        title: z.string(),
        year: z.string(),
        single: z.boolean(),
        artwork: z.string(),
        link: z.string(),
      })
    ),
  }),
});

const blogCollection = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    date: z.date(),
    images: z.array(z.string()),
    categories: z.array(z.string()),
    featured: z.boolean().optional(),
    summary: z.string(),
  }),
});

const aboutCollection = defineCollection({
  type: "content",
});

const workspaceCollection = defineCollection({
  type: "data",
  schema: z.object({
    laptop: z.array(
      z.object({
        name: z.string(),
        description: z.string(),
        image: z.string(),
        link: z.string(),
      })
    ),
    coding: z.array(
      z.object({
        name: z.string(),
        description: z.string(),
        image: z.string(),
        link: z.string(),
      })
    ),
    music: z.array(
      z.object({
        name: z.string(),
        description: z.string(),
        image: z.string(),
        link: z.string(),
      })
    ),
    video: z.array(
      z.object({
        name: z.string(),
        description: z.string(),
        image: z.string(),
        link: z.string(),
      })
    ),
  }),
});

export const collections = {
  music: musicCollection,
  blog: blogCollection,
  about: aboutCollection,
  workspace: workspaceCollection,
};
