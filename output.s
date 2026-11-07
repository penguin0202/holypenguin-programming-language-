	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"<string>"
	.def	main;
	.scl	2;
	.type	32;
	.endef
	.text
	.globl	main
	.p2align	4
main:
.seh_proc main
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	callq	__main
	movl	$600, %edx
	addl	$500, %edx
	leaq	.L.print_fmt(%rip), %rcx
	callq	printf
	movl	$0, -4(%rbp)
	leaq	.L.input_fmt(%rip), %rcx
	leaq	-4(%rbp), %rdx
	callq	scanf
	movl	-4(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -4(%rbp)
	movl	-4(%rbp), %edx
	leaq	.L.print_fmt(%rip), %rcx
	callq	printf
.LBB0_1:
	callq	getchar
	movl	%eax, %ecx
	cmpl	$10, %ecx
	sete	%al
	cmpl	$-1, %ecx
	sete	%cl
	orb	%cl, %al
	testb	$1, %al
	jne	.LBB0_2
	jmp	.LBB0_1
.LBB0_2:
	leaq	.L.pause_fmt(%rip), %rcx
	callq	printf
	callq	getchar
	xorl	%eax, %eax
	addq	$48, %rsp
	popq	%rbp
	retq
	.seh_endproc

	.section	.rdata,"dr"
.L.print_fmt:
	.asciz	"%d\n"

.L.input_fmt:
	.asciz	"%d"

	.p2align	4, 0x0
.L.pause_fmt:
	.asciz	"Press any key to continue . . ."

