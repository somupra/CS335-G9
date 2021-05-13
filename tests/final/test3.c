int main(){
	int a, b, c, d, e;
	d = 5;
	e = 5;
	a = 7 ;
	b = a ;

	do{
		b = a+1 ;
		a++;
		c = b*a ;
		d = b/a ;
		printf("%d, %d, %d\n", c, d);
	}

	while(a<10) ;
	return 0 ;
}
