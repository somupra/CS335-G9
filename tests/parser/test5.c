long area(int length, int breadth)
{
	long a;
	a = (long)length*(long)breadth;
	return a;
}
long perimeter(int length, int breadth)
{
	return 2*length+2*breadth;
}
int main(){
	int l=2,b=20;
	long a = area(l,b);
	long p = perimeter(l,b);
	return 0;
}
