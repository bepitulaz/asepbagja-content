# Comments: Introduction to Functional Programming in JavaScript (Part 1)

**Article:** [Introduction to Functional Programming in JavaScript (Part 1)](content/blog/en/introduction-to-functional-programming-in-javascript-part-1.md)
**Total comments:** 6

---

**Roman Storm** · 2016-07-03

Have you looked at TypeScript? [https://www.typescriptlang....](https://www.typescriptlang.org/) - I think FP is way better with TypeScript and at the end of the day, it's complied down to JS.

---

**Matvey** · 2016-07-03 ↩ *reply to Roman Storm*

Hello, Could you give me an answer "What case is the most suitable for TypeScript?" or give me a link to sources where someone answer this.

---

**Asep Bagja Priandana** · 2016-07-03 ↩ *reply to Roman Storm*

Yes, I knew about TypeScript. Honestly I love Clojurescript for doing FP that can compile down to JS. Since this post is about introduction to FP, hence I use the regular JavaScript to explain.

---

**Csongor** · 2016-07-04

I think the comment about the changing i in the impureFunction() distracts the focus. I think the following example would help more in focusing to the point:

'use strict';

let sample = [1, 2, 3]; // I want each element of this array add by 1.

function impureFunction(data) {
    data[0]=99;
    return data;
}

let result = impureFunction(sample);
console.log(result); // You get what you want: [99, 2, 3]
console.log(sample); // But you get the side effect too. The value has been changed. This prints [99, 2, 3] too.

What do you think?

---

**Asep Bagja Priandana** · 2016-07-04 ↩ *reply to Csongor*

I think you are right. It will be better to delete the comment. The focus is not there actually.

---

**Nguyen Anh Duc** · 2016-07-08

The snippet that has recursive to avoid side impact is not convincing enough to me. In the recursive version, you passed in an array that is used to store the new value.
We can do the same thing with the impureFunction

function impureFunction(data) {
  let result = []
  for(let i=0; i < data.length; i++) {
    result[i] = data[i] + 1;
  }
  return result;
}

let result = impureFunction(sample);
console.log(result); // You get what you want: [2, 3, 4]
console.log(sample); // You also get what you want [1, 2, 3]

---
