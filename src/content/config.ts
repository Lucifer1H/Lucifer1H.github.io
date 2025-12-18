import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
    schema: z.object({
        title: z.string(),
        description: z.string().optional(),
        // Support both date and pubDate
        pubDate: z.coerce.date().optional(),
        date: z.coerce.date().optional(),
        updatedDate: z.coerce.date().optional(),
        heroImage: z.string().optional(),
        tags: z.array(z.string()).default([]),
    }).transform((data) => ({
        // Normalize date to pubDate
        ...data,
        pubDate: data.pubDate || data.date || new Date(),
    })),
});

export const collections = { blog };
