(require
  hyrule.macrotools [defmacro!])

(import
  sys
  importlib.util
  itertools
  hy.scoping [ScopeLet]
  hyrule.collections [by2s]
  hyrule.macrotools [map-hyseq])


(defmacro comment [#* body]

  #[=[Ignore any arguments and expand to ``None``. ::

    (setv x ["a"
             (comment <h1>Surprise!</h1>
                      You might be surprised what's lexically valid in Hy
                      (keep delimiters balanced and you're mostly good to go))
             "b"])
     x  ; => ["a" None "b"]

  Contrast with Hy's built-in semicolon comments and :ref:`discard
  prefix <hy:discard-prefix>`::

    (setv x [1 ; 2 3
               3])
    x  ; => [1 3]
    (setv x [1 #_ 2 3])
    x  ; => [1 3]
    (setv x [1 (comment 2) 3])
    x  ; => [1 None 3]]=]

  None)


(defn constantly [value]
  "Return a constant function, which ignores its arguments and always
  returns ``value``. ::

    (setv answer (constantly 42))
    (answer)           ; => 42
    (answer 1 :foo 2)  ; => 42"
  (fn [#* args #** kwargs]
    value))


(defn dec [n]
  #[[Shorthand for ``(- n 1)``. The name stands for "decrement".]]
  (- n 1))


(defn inc [n]
  #[[Shorthand for ``(+ n 1)``. The name stands for "increment".]]
  (+ n 1))


(defn import-path [path [name None]]

  #[[Import the Python or Hy source code at ``path`` as a module with
  :func:`importlib.util.spec_from_file_location`, per Python's documentation.
  Return the new module object. ``name`` defaults to ``(str (hy.gensym
  "import-path"))``. ::

    (setv p (hy.I.pathlib.Path "mymodule.hy"))
    (.write-text p "(setv foo 3)")
    (setv m (import-path p))
    (print m.foo)  ; => 3]]

  (when (is name None)
    (setv name (str (hy.gensym "import-path"))))
  (when (in name sys.modules)
    (raise (ValueError f"The name {(hy.repr name)} is already in use in `sys.modules`.")))

  ; Translated from https://github.com/python/cpython/blob/408e127159e54d87bb3464fd8bd60219dc527fac/Doc/library/importlib.rst?plain=1#L1584
  (setv spec (importlib.util.spec-from-file-location name path))
  (setv m (importlib.util.module-from-spec spec))
  (setv (get sys.modules name) m)
  (.loader.exec-module spec m)

  m)


(defmacro of [base #* args]

  "Shorthand for type annotations with indexing. If only one argument
  is given, the macro expands to just that argument. If two arguments are
  given, it expands to indexing the first argument with the second.
  Otherwise, the first argument is indexed using a tuple of the rest. Thus:

  - ``(of T)`` becomes ``T``.
  - ``(of T x)`` becomes ``(get T x)``.
  - ``(of T x y z)`` becomes ``(get T #(x y z))``.

  Here are some Python equivalents of example uses:

  - ``(of str)`` → ``str``
  - ``(of List int)`` → ``List[int]``
  - ``(of Callable [int str] str)`` → ``Callable[[int, str], str]``"

  (if
    (not args) base
    (if (= (len args) 1)
        `(get ~base ~@args)
        `(get ~base #(~@args)))))


(defn parse-args [spec [args None] #** parser-args]

  #[=[Shorthand for typical uses of :py:mod:`argparse`. ``spec`` is a list of arguments to pass in repeated calls to :py:meth:`ArgumentParser.add_argument <argparse.ArgumentParser.add_argument>`. ``args``, defaulting to :data:`sys.argv`, will be used as the input arguments. ``parser-args``, if provided, will be passed on to the constructor of :py:class:`ArgumentParser <argparse.ArgumentParser>`. The return value is that of :py:meth:`parse_args <argparse.ArgumentParser.parse_args>`.

  ::

    (parse-args :spec [["strings" :nargs "+" :help "Strings"]
                       ["-n" "--numbers" :action "append" :type int :help "Numbers"]]
                :description "Parse strings and numbers from args"
                :args ["a" "b" "-n" "1" "-n" "2"])
       ; => Namespace(strings=['a', 'b'], numbers=[1, 2])]=]

  (import argparse)
  (setv parser (argparse.ArgumentParser #** parser-args))
  (for [arg spec]
    (setv positional-arguments []
          keyword-arguments []
          value-of-keyword? False)
    (for [item arg]
      (if value-of-keyword?
          (.append (get keyword-arguments -1) item)
          (if (isinstance item hy.models.Keyword)
              (.append keyword-arguments [item.name])
              (.append positional-arguments item)))
      (setv value-of-keyword? (and
        (not value-of-keyword?)
        (isinstance item hy.models.Keyword))))
    (parser.add-argument #* positional-arguments #** (dict keyword-arguments)))
  (.parse-args parser args))


(defmacro pun [#* body]
  #[[Evaluate ``body`` with a shorthand for keyword arguments that are set to variables of the same name. Any keyword whose name starts with an exclamation point, such as ``:!foo``, is replaced with a keyword followed by a symbol, such as ``:foo foo``::

    (setv  a 1  b 2  c 3)
    (pun (dict :!a :!b :!c))
      ; i.e., (dict :a a :b b :c c)
      ; => {"a" 1  "b" 2  "c" 3}

  This macro is named after the `NamedFieldPuns <https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/record_puns.html>`__ language extension to Haskell.]]

  (map-hyseq `(do ~@body) _pun))

(defn _pun [x]
  (itertools.chain.from-iterable (gfor
    e x
    (if (and (isinstance e hy.models.Keyword) (.startswith e.name "!"))
      [(hy.models.Keyword (cut e.name 1 None))
        (hy.models.Symbol (cut e.name 1 None))]
      [(map-hyseq e _pun)]))))


(do-mac (do
  (setv code "
      (cond
        (< x 0) -1
        (> x 0)  1
        (= x 0)  0
        True     (raise TypeError))")

  `(defn sign [x]
    ~f"Return -1 for negative ``x``, 1 for positive ``x``, and 0 for
    ``x`` equal to 0. The implementation is exactly ::

    {code}

    with the corresponding consequences for special cases like negative
    zero and NaN."

      ~(hy.read code))))


(defn xor [a b]

  "A logical exclusive-or operation.

  - If exactly one argument is true, return it.
  - If neither is true, return the second argument (which will
    necessarily be false).
  - Otherwise (that is, when both arguments are true), return
    ``False``.

  ::

    [(xor 0 0) (xor 0 1) (xor 1 0) (xor 1 1)]
      ; => [0 1 1 False]"

  (if (and a b)
    False
    (or a b)))

(defmacro smacrolet [_hy_compiler bindings #* body]
  #[=[Tell the Hy compiler to translate certain symbols when compiling the body. The effect is similar to symbol macros (as seen in e.g. Common Lisp) and uses the same scoping logic as :hy:func:`let`, hence the name ``smacrolet``, i.e., "symbol macro let". The first argument is a list of bindings, which must be pairs of symbols. ::

    (setv x "a")
    (setv y "other")
    (smacrolet [y x  z x]
      (+= y "b")
      (+= z "c"))
    (print x)  ; "abc"
    (print y)  ; "other"

  The translation doesn't occur in uses of the symbol that wouldn't apply to a :hy:func:`let` binding. Here, for example, ``a`` in an attribute assignment isn't replaced::

    (setv x 1)
    (smacrolet [a x]
      (defclass C []
        (setv a 2))
      (print a))  ; 1
    (print C.a)   ; 2]=]

  (when (% (len bindings) 2)
    (raise (ValueError "bindings must be paired")))

  (setv scope (.scope.create _hy_compiler ScopeLet))
  (for [[target value] (by2s bindings)]
    (when (not (isinstance value hy.models.Symbol))
      (raise (ValueError "Bind target value must be a Symbol")))
    (when (not (isinstance target hy.models.Symbol))
      (raise (ValueError "Bind target must be a Symbol")))
    (when (in '. target)
      (raise (ValueError "Bind target must not contain a dot")))
    (.add scope target (str value)))
  (with [scope]
    (.compile _hy_compiler `(do ~@body))))
