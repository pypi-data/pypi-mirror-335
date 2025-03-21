#include "list.h"
#include <stdlib.h>

/**
 * Removes all references to an item from a list
 *
 * Parameters
 * ----------
 * list**
 *    Pointer to the start of a list
 * ptr : void*
 *    Item to look for and remove
 *
 * Returns
 * -------
 * int
 *     Number of items removed or an error code:
 *         -1 = list == NULL
 *         -2 = *list == NULL
 */
int remove_from_list(ListItem **list, void* ptr) {
    ListItem *current = *list;
    ListItem *prev = NULL, *next=NULL;
    int removed = 0;
    if(list == NULL) return -1;
    if(*list == NULL) return -2;

    while(current != NULL){
        if(current->ptr == ptr) { // found the item to remove
            if(prev == NULL) { // it is the first element
                if(current->next){ // there is an item next in the list
                    *list = current->next; // so make it first
                } else {
                    *list = NULL; // only a single item in the list
                }
            } else {
                if(current->next != NULL){ // there is an item next in the list
                    prev->next = current->next; // set the prev to point to the next
                } else {
                    prev->next = NULL; // end the list
                }
            }
            removed++;
            // just update next, as previous will still be the previous one
            next = current->next;
            free(current);
            current = next;
        } else {
            prev = current;
            current = current->next;
        }
    }
    return removed;
}
