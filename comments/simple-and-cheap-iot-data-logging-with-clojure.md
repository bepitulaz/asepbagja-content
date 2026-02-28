# Comments: Simple, Cheap, and Scalable IoT Data Logging With Clojure

**Article:** [Simple, Cheap, and Scalable IoT Data Logging With Clojure](content/blog/en/simple-and-cheap-iot-data-logging-with-clojure.md)
**Total comments:** 3

---

**Tim McCoy** · 2015-12-08

Ahhh - the things you can do when the database fits into memory. I am writing similar code but there are some use cases where the file will be too big. Yet I don't really need a database....since the file containing the data is not intended to be shared and the few queries I need to run are simple logic. Thanks for taking the time to show your example.

---

**Asep Bagja Priandana** · 2015-12-08 ↩ *reply to Tim McCoy*

In my case, the log file per day is small enough. Thanks for reading my article :)

---

**Tim McCoy** · 2015-12-08 ↩ *reply to Asep Bagja Priandana*

Well my son & I were discussing this topic (of logging) over recent holiday. He is a Java developer and in graduate school - so he's hard to argue with (although father & son usually are...) I am winning him over to Clojure easily. We were discussing how application servers keep session state in a RDBMS. I was telling him that it would be much simpler to use something like Datomic or even simply doing what you are doing. Why use transaction logic when you simply want to append the new state with a timestamp? I told him that if we thought about how many times we use over-engineered RDBMS to perform such tasks because we have it - so why not? But now I understand how this multiplies complexity of the application. Great for contractors - bad for the user's business. Kind regards.

---
