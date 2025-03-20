docs = {
   "python": "https://docs.python.org/3/",
   "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
   "java": "https://docs.oracle.com/en/java/",
   "c#": "https://learn.microsoft.com/en-us/dotnet/csharp/",
   "c++": "https://learn.microsoft.com/en-us/cpp/cpp/?view=msvc-170",
   "php": "https://www.php.net/docs.php",
   "ruby": "https://www.ruby-lang.org/en/documentation/",
   "swift": "https://swift.org/documentation/",
   "r": "https://cran.r-project.org/manuals.html",
   "sql": "https://www.w3schools.com/sql/",
   "kotlin": "https://kotlinlang.org/docs/home.html",
   "typescript": "https://www.typescriptlang.org/docs/", 
   "go": "https://go.dev/doc/",
   "rust": "https://www.rust-lang.org/learn",
   "scala": "https://docs.scala-lang.org/",
   "dart": "https://dart.dev/docs", 
   "perl": "https://perldoc.perl.org/"
}

def language_help(language):
   """
   Returns a link for useful information given a programming language.
   """
   if not isinstance(language, str):
      return "Error: Please provide a language name as a string."

   language = language.lower()
   if language in docs:
      return docs[language]
   return f"Help not available for {language}. Try one of the following: {', '.join(docs.keys())}"