	.file	"<string>"
	.section	.ltext,"axl",@progbits
	.globl	main
	.p2align	4
	.type	main,@function
main:
	.cfi_startproc
	pushq	%rax
	.cfi_def_cfa_offset 16
	movl	$0, 4(%rsp)
	movl	$6, 4(%rsp)
.LBB0_1:
	jmp	.LBB0_1
	.cfi_def_cfa_offset 8
	movl	$5, %eax
	addl	$5, %eax
	cmpl	$7, %eax
	jle	.LBB0_5
	jmp	.LBB0_5
.LBB0_5:
	xorl	%eax, %eax
	popq	%rcx
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc

	.section	".note.GNU-stack","",@progbits
