# Comments: Convert Float to Char Then Concatenate It in Arduino

**Article:** [Convert Float to Char Then Concatenate It in Arduino]((unknown))
**Total comments:** 2

---

**lynxluna** · 2016-04-25

Will it run if we change it with decimal placement like

sprintf(buff, "somedata %.2f", 2.0f)

Will it work?

---

**Asep Bagja Priandana** · 2016-04-26 ↩ *reply to lynxluna*

No, it won't work. It will print "somedata ?". sprintf in Arduino is not supporting float.

---
