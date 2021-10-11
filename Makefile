TARGET   = firesim.out
CC       = g++
CCFLAGS  = -g -pedantic -Wall -Werror
LDFLAGS  = -lm
SOURCES  = $(wildcard *.cpp)
INCLUDES = $(wildcard *.hpp)
OBJECTS  = $(SOURCES:.c=.o)

all:$(TARGET)

$(TARGET):$(OBJECTS)
	$(CC) -o $(TARGET) $(LDFLAGS) $(OBJECTS)

$(OBJECTS):$(SOURCES) $(INCLUDES)
	$(CC) -c $(CCFLAGS) $(SOURCES)

clean:
	rm -f $(TARGET) $(OBJECTS)
