; Basic Hello World 
(write-line "Hello World!")
(format t "Created By Tirthraj Mahajan") ; For printing formatted strings
(print "How are you!")
(terpri)        ;Prints a newline to the command line.

(defvar my-list 1)
(defvar add-one (+ 1 0))
(defvar ans 1)
(defvar I 0)

(defvar x 234)
(defvar y 123)
(print x)

; setq is used to set the value of an existing variable
(setq x 10)
(print x)

; Since there is no type declaration for variables in LISP, you directly specify a value for a symbol with the setq construct.
(setq y 20)
(print y)

;In LISP, constants are variables that never change their values during program execution. Constants are declared using the defconstant construct.
(defconstant PIE 3.141592)
(print PIE)
; Try Changing the value of constant
; (setq PI 3) ; ERROR: SETQ: PI is a constant, may not be used as a variable

; Local Variables are defined within a given procedure
; Like the global variables, local variables can also be created using the setq construct.
; There are two other constructs - let and prog for creating local variables.

( let ( (message1 "This is message 1") (message2 "And it is lexically Scoped") )
    (print message1)
    (print message2)
)

(setq i 0)
(loop
  (format t "Iteration ~a~%" i)
  (incf i 1) ; or (setq i (+ i 1))
  (when (>= i 10)
    (return i)))

(dotimes (n 11)
   (format t "~d : ~d ~%" n (* n n))
)

(defun fac(n)
    (if (= n 0) 
        1                   ; if block
        (* n (fac (- n 1)) )    ; else block
    )
)

(dotimes (num 11) (format t "Factorial of ~d : ~d ~%" num (fac num)))


; Cons as LIST
(print (cons 1 (cons 2 (cons 3 nil))))
(print (list 1 2 3))

; Printing CAR
(print (car '(1 2 3)))
(print (car (cons 1 (cons 2 (cons 3 nil)))))

; Printing CDR 
(print (cdr '(1 2 3)))
(print (cdr (cons 1 (cons 2 (cons 3 nil)))))


; Mixing CAR and CDR
(print (car (cdr (cdr '(1 2 3 4 5 6 7 ED)))))

; Modifying a List
(setq my-list '(1 2 3 4))
(setf (nth 2 my-list) 42) ; Sets the third element of my-list to 42
(print my-list)           ; Prints (1 2 42 4)

(print ((lambda (x y) (* x y)) 10 20))

; Creates an anonymous function and assigns it to a variable
(setq add-one (lambda (x) (+ x 1)))

; To call the function, we use 'funcall' function, which calls the function dynamically
(print (funcall add-one 10))

(defun fac(num) 
"This fn finds factorial"

(setq ans 1)
(loop 
    (if (<= num 0) (return ans))
    (setq ans (* ans num))
    (decf num)
)

)

(loop for i from 0 to 10
    do(format t "~d : ~d ~%" i (fac i))
)

