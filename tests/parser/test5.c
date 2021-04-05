int area(int length, int breadth)
{
	int a;
	a = (int)length*(int)breadth;
	return a;
}
int perimeter(int length, int breadth)
{
	return 2*length+2*breadth;
}
int main(){
	int l=2,b=20;
	int a = area(l,b);
	int p = perimeter(l,b);
	return 0;
}
