# Comments: Add Free SSL to Existing WordPress Site with Docker and Let's Encrypt

**Article:** [Add Free SSL to Existing WordPress Site with Docker and Let's Encrypt](content/blog/en/add-free-ssl-to-existing-wordpress-site-with-docker-and-lets-encrypt.md)
**Total comments:** 3

---

**Jonathon Howey** · 2016-06-29

You may want to put more detail into Step 2.. its the main part of the article your Title calls out. otherwise you should name this "How to move Wordpress to Docker with SSL".
Describe how the images interact, etc.

---

**Asep Bagja Priandana** · 2016-07-01 ↩ *reply to Jonathon Howey*

Thanks for your advice @jonathonhowey:disqus. I have updated the article and wrote more detail for the step 2 :)

---

**Jonathon Howey** · 2016-07-01 ↩ *reply to Asep Bagja Priandana*

Looks much more detailed.  :).
 If you get time, in context of #2, you may also want to explain:
* How Nginx is actually configured to use the Certs being generated/signed (also see next point) .. or just hint to reader the jwilder/nginx-proxy image is already doing so and and point them there
* That the vhost.d volume has the configurations for your Wordpress image in #5 (maybe provide sample?)

I say this because it's a "How To" article which means you're probably targeting folks with very little NGINX experience.

---
