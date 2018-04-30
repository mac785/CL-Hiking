import cv2
from copy import deepcopy
from tkinter import filedialog
from enum import Enum
import random
import numpy as np

class ClickHandlerMode(Enum):
    FIRST_CLICK = 0
    SECOND_CLICK = 1
    SEARCHING = 2
    DONE = 3

ALPHA = 100.0  # play with this number to decide how important the altitude data is!

class Pathmaker():
    def __init__(self):
        print("Showing file dialog. Make sure it isn't hiding!")
        root = filedialog.Tk()
        root.withdraw()
        map_filename = filedialog.askopenfilename(title="Find the heightmap.")
        # map_filename = "new_england height map.jpg"
        if map_filename == "":
            raise IOError("No file found...")
        self.original_map = cv2.imread(map_filename,cv2.IMREAD_GRAYSCALE)
        self.drawing_map = cv2.cvtColor(self.original_map, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Map",self.drawing_map)


    def start_process(self):
        """
        this is essentially our game loop - it sets up the mouse listener,
        and then enters an infinite loop where it waits for the user to select
        the two cities before it performs a search and displays the result.
        :return:
        """
        #if anybody does anything mouse-related in the "Map" window,
        # call self.handleClick.
        cv2.setMouseCallback("Map", self.handleClick)
        self.reset()
        while True:
            while self.click_mode != ClickHandlerMode.SEARCHING:
                cv2.waitKey(1)
            path = self.perform_search()
            self.drawing_map = cv2.cvtColor(self.original_map, cv2.COLOR_GRAY2BGR)
            self.draw_start_point()
            self.draw_end_point()
            self.display_path(path)
            cv2.imshow("Map",self.drawing_map)

            # TODO: consider the following. No action is required.
            # Optional: if you would like to save a copy of the graphic that results,
            # you can say:
            #  cv2.imsave("pickAFilename.png",self.drawing_map).


            print("Click on screen once to start again.")
            self.click_mode = ClickHandlerMode.DONE

    def get_height_at(self,point):
        """
        Note: I've written this convenience method to illustrate the conversion
        from 0-255 to 0.0 to 1.0.
        :param point: a location in (r,c) format.
        :return: a value from 0.0 - 1.0 representing the brightness (height) at
        this point.
        """
        return self.original_map[point[0]][point[1]]/255.0

    def set_color_at(self,color,point):
        """
        changes the color of drawing_map at the given (r,c) point to the color
        (b,g,r) in range 0-255.
        Note: you will still need to imshow the display map for this change to be
        seen by the user.
        :param color: a 0-255 color in format (b, g, r)
        :param point:  a point in format (r,c)
        :return: None
        """
        self.drawing_map[point[0]][point[1]] = color

    def reset(self):
        self.click_mode = ClickHandlerMode.FIRST_CLICK
        self.drawing_map = cv2.cvtColor(self.original_map, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Map", self.drawing_map)

    def draw_start_point(self):
        """
        draws a marker on the self.drawing_map at location self.start_point_x_y.
        Note that the cv2 drawing functions work in (x,y) coords, not (r,c)!
        :return: None
        """
        cv2.circle(self.drawing_map, center=self.start_point_x_y, radius=10,
                   color=(0, 192, 0), thickness=1)
        cv2.line(self.drawing_map, (self.start_point_x_y[0] - 10, self.start_point_x_y[1]),
                 (self.start_point_x_y[0] + 10, self.start_point_x_y[1]),
                 color=(0, 192, 0), thickness=1)
        cv2.line(self.drawing_map, (self.start_point_x_y[0], self.start_point_x_y[1] - 10),
                 (self.start_point_x_y[0], self.start_point_x_y[1] + 10),
                 color=(0, 192, 0), thickness=1)

    def draw_end_point(self):
        """
        draws a marker on the self.drawing_map at location self.end_point_x_y.
        Note that the cv2 drawing functions work in (x,y) coords, not (r,c)!
        :return: None
        """
        cv2.circle(self.drawing_map, center=self.end_point_x_y, radius=10,
                   color=(0, 0, 192), thickness=1)
        cv2.line(self.drawing_map, (self.end_point_x_y[0] - 10, self.end_point_x_y[1]),
                 (self.end_point_x_y[0] + 10, self.end_point_x_y[1]),
                 color=(0, 0, 192), thickness=1)
        cv2.line(self.drawing_map, (self.end_point_x_y[0], self.end_point_x_y[1] - 10),
                 (self.end_point_x_y[0], self.end_point_x_y[1] + 10),
                 color=(0, 0, 192), thickness=1)

    def handleClick(self,event,x,y,flags,param):
        """
        this method gets called whenever the user moves or clicks or does
        anything mouse-related while the mouse is in the "Map" window.
        In this particular case, it will only do stuff if the mouse is being
        released. What it does depends on the self.click_mode enumerated variable.
        :param event: what kind of mouse event was this?
        :param x:
        :param y:
        :param flags: I suspect this will be info about modifier keys (e.g. shift)
        :param param: additional info from cv2... probably unused.
        :return: None
        """
        if event == cv2.EVENT_LBUTTONUP: #only worry about when the mouse is released inside this window.
            if self.click_mode == ClickHandlerMode.FIRST_CLICK:
                # we were waiting for the user to click on the first city, and she has just done so.
                # identify which city was selected, set the self.first_city_id variable
                # and display the selected city on screen.
                self.start_point_x_y = (x,y)
                self.start_point_r_c = (y,x)
                self.draw_start_point()

                # update the screen with these changes.
                cv2.imshow("Map", self.drawing_map)
                # now prepare to receive the second city.
                self.click_mode = ClickHandlerMode.SECOND_CLICK
                return

            elif self.click_mode == ClickHandlerMode.SECOND_CLICK:
                # we were waiting for the user to click on the second city, and she has just done so.
                # identify which city was selected, set the self.second_city_id variable
                # and display the selected city on screen.
                self.end_point_x_y = (x,y)
                self.end_point_r_c = (y,x)
                self.draw_end_point()
                #update the screen with these changes
                cv2.imshow("Map", self.drawing_map)
                # now prepare for the search process. Any further clicks while
                #   the search is in progress will be used to advance the search
                #   step by step.
                self.click_mode = ClickHandlerMode.SEARCHING
                return

            elif self.click_mode == ClickHandlerMode.SEARCHING:
                #advance to the next step
                self.waiting_for_click = False
                return

            elif self.click_mode == ClickHandlerMode.DONE:
                # we just finished the search, and user has clicked, so let's start over
                self.reset()
                return

    def wait_for_click(self):
        """
        makes the program freeze until the user releases the mouse in the window.
        :return: None
        """
        self.waiting_for_click = True
        while self.waiting_for_click:
            cv2.waitKey(1)

    def display_path(self, path_terminator, color = (0,192,255)):
        """
        draws the edges that connect the cities in the list of cities in a
         color that makes them obvious. If the path is None, then you should
         display a message that indicates that there is no path.
         Modifies the existing self.drawing_map graphics variable.
        :param path: a list of city ids or None, if no path can be found.
        :return: None
        """
        # -----------------------------------------
        # TODO: You should write this method
        path_location = path_terminator
        while(path_location[0] != self.start_point_r_c[0]):
            self.set_color_at(color, path_location)
            path_location = [int(self.record[path_location[0],path_location[1],[1]]), int(self.record[path_location[0],path_location[1],[2]])]
        self.set_color_at(color, path_location)
        # The way I did it in the transit project:
        # for i in range(0,len(path)-1):
        #     self.draw_edge(self.current_map,path[i],path[i+1],[255,0,0])
        # cv2.imshow("Map", np.repeat(np.repeat(self.current_map, 2, axis=0), 2, axis=1))

        # while(self.record[path_terminator[0],path_terminator[1],])

        # -----------------------------------------

    def cost(self,point1,point2,dist=1.0):
        """
        gives a numerical value that indicates the cost of the single step from point1 to point2, based on both lateral
        and altitude information.
        :param point1: the location of a pixel on the map
        :param point2: the location of an adjacent pixel on the map
        :param dist: the distance between the two pixels, probably 1.00 or 1.41.
        :return: the cost function - how expensive is it to move from pixel1 to pixel2?
        """
        result = 0
        # ------------------------------------------
        # TODO: You should write this method
        result = dist + ALPHA*abs(self.get_height_at(point1) - self.get_height_at(point2))
        # ------------------------------------------

        return result

    def heuristic(self,point):
        """
        gives a numerical value that is NO MORE than the least possible cost of the path from this point to self.end_point.
        :param point: a location in (r,c) coords
        :return:
        """
        result = 0
        #------------------------------------------
        # TODO: You should write this method
        # I recommend using the euclidean or manhattan distance from point to self.end_point_r_c.
        # print("--------")
        # print(point[0])
        # print(self.end_point_r_c[0])
        # print(point[1])
        # print(self.end_point_r_c[1])
        # print("--------")

        result = np.sqrt((pow(point[0]-self.end_point_r_c[0],2))+(pow(point[1]-self.end_point_r_c[1],2)))

        #------------------------------------------
        return result

    def get_unvisited_neighbors(self,pt):
        """
        :param pt: an in-bounds point as (r,c)
        :return: a list of points to investigate along with a weight corresponding
        to the distance from pt to this point.
        """
        neighbors = []
        for i in range(-1,2):
            for j in range(-1,2):
                if i == 0 and j == 0:
                    continue
                if (pt[0]+i,pt[1]+j) in self.visited:
                    continue
                if pt[0]+i<0 or pt[0]+i >= self.original_map.shape[0] or\
                    pt[1]+j<0 or pt[1]+j >= self.original_map.shape[1]:
                    continue
                # if i or j is zero, then this is a N,S,E,W path, and should have weight 1.
                if i*j == 0:
                    neighbors.append(((pt[0]+i,pt[1]+j),1.0))
                # .... otherwise, this is a diagonal move, and we want weight sqrt(2).
                else:
                    neighbors.append(((pt[0]+i,pt[1]+j),1.414))
        return neighbors

    def draw_heat_map(self):
        """
        An optional debugging tool that might be helpful - it draws a visual representation of the first layer of
        self.record in a window called "Heat".
        I wouldn't do this EVERY frame... it will slow the search down A LOT. But every now and then it might be helpful.
        :return: None
        """
        heat_map = np.zeros(self.record.shape, dtype=float)
        heat_map[:, :, 0] = (self.record[:, :, 0] % 180) * (self.record[:, :, 0] < 9E9)
        heat_map[:, :, 1] = 255.0
        heat_map[:, :, 2] = 255 * (self.record[:, :, 0] < 9E9)
        heat_map = cv2.cvtColor(heat_map.astype(np.uint8), cv2.COLOR_HSV2BGR)
        heat_map[:, :, 0] += (self.record[:, :, 0] >= 9E9) * (self.original_map[:, :])
        heat_map[:, :, 1] += (self.record[:, :, 0] >= 9E9) * (self.original_map[:, :])
        heat_map[:, :, 2] += (self.record[:, :, 0] >= 9E9) * (self.original_map[:, :])

        cv2.imshow("Heat", heat_map)
        cv2.waitKey(1)

    def perform_search(self):
        """
        Uses the A* algorithm to try to detect the optimal path from self.start_point to self.end_point.
        :return: either the self.end_point, if we found a path, or None - if we didn't.
        """
        start = self.start_point_r_c
        end = self.end_point_r_c

        # I recommend that you use a list of two-element lists for frontier, where the first element is the "f" value,
        # and the second is the point (a two-element list in its own right). If you tell frontier to .sort(), it will
        # sort by the first element, which allows you to make this act like a Priority Queue, but one that you can search
        # for a point. (Alternately, you can just linear search the unsorted list for the lowest f value - you'll have to
        # decide which one is faster, but note that the internal "sort()" command may run faster than if you wrote it yourself.)
        frontier = []

        # please use these data structures for visited and record so that they work with other parts of the program nicely.
        self.visited = []
        #self.record is a 3-d array of the same size as the map, three "layers" deep.
        self.record = np.zeros((self.original_map.shape[0],self.original_map.shape[1],3),dtype = float)
        self.record[:,:,0] = 9E9  # first "layer" of the record map is the distance travelled to get to this \
                                                    # point from the start
        self.record[:,:,1] = -1 # second and third "layers" are the point from which we arrived.
        self.record[:,:,2] = -1

        # ------------------------------------------
        # TODO: You need to write the rest of this method.
        # consider what you need to do before you loop through the search cycle.

        self.record[start[0],start[1],0] = 0
        frontier.append([0+self.heuristic(start), start])

        # loop while there are still elements in frontier.
        # draw = 0
        lap = 0
        while len(frontier) != 0:
            lap += 1
            frontier.sort()
            f, pt = frontier.pop(0)
            if len(self.visited) % 100 == 0:
                self.display_path(pt,(random.randint(64,255),random.randint(64,255),random.randint(64,255)))
                cv2.imshow("Map", self.drawing_map)
                self.draw_heat_map()
            if pt == end:
                print("Made it to the end in lap:")
                print(lap)
                return pt
                break
            neighbors = self.get_unvisited_neighbors(pt)
            for i in neighbors:
                # print("Inside neighbor loop")
                # calculate gp2 = gpt + cost
                # I think I want to change pt[0] and pt[1] in the line below to be i[0] or some permutation of that
                # print(self.cost(pt,i[0]))
                newG = self.record[pt[0],pt[1],0] + self.cost(pt,i[0])
                # if gpt2 is better than record's g @ pt2, path_terminator
                # print("New G")
                # print (newG)
                # print("Record")
                # print(self.record[i[0][0],i[0][1],0])
                if(newG < self.record[i[0][0],i[0][1],0]):
                    # print("Inside If statement")
                    # update record with better value pt
                    self.record[i[0][0]][i[0][1]][1] = pt[0]
                    self.record[i[0][0]][i[0][1]][2] = pt[1]
                    self.record[i[0][0]][i[0][1]][0] = newG
                    # calculate hpt2
                    # print(self.heuristic(i[0]))
                    newH = self.heuristic(i[0])
                    # calculate fpt2 = hpt2 + gpt2
                    newF = newG + newH
                    # add or update frontier with (fpt2, pt2)
                    # print("Frontier Before")
                    # print(frontier)
                    frontier.append([newF, i[0]])
                    # print("Frontier After")
                    # print(frontier)
            # print(frontier)

        # # optional - if you are using the list as a priority queue, you might find this code helpful.
        # # this is the equivalent of popping from a minheap priority queue.... sorted by the first value in the list.
        # # ---------------------
        # frontier.sort()
        # f, pt = frontier[0]
        # del (frontier[0])
        # # ---------------------

        # optional... every few (100?) loops, draw the path that lead to pt and update a "heat map" that shows what
        #  self.record looks like. You might find this interesting to observe what is going on as the computer works.
        # if len(self.visited) % 100 == 0:
        #     self.display_path(pt,(random.randint(64,255),random.randint(64,255),random.randint(64,255)))
        #     cv2.imshow("Map", self.drawing_map)
        #
        #     self.draw_heat_map()

        # ------------------------------------------
        return None
# -----------------------------------------------------------------------------------------------------------------
# This is what the program will actually do.... like Java's main() method. (Since it's not inside the class declaration.)
pathmaker = Pathmaker()
pathmaker.start_process()

# traditionally, this will wait indefinitely until the user presses a key and
# then close the windows and quit. The loop in this program will make it so that
# it never really gets here, but it's a good habit.
cv2.waitKey()
cv2.destroyAllWindows()
