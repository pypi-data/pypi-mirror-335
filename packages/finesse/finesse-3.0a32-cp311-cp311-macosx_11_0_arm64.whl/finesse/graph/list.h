#ifndef LIST_H
#define LIST_H

typedef struct ListItem ListItem;

struct ListItem {
    void*  ptr;
    ListItem *next;
};

int remove_from_list(ListItem **list, void* ptr);

#endif
